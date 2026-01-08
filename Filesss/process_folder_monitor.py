"""
Folder Monitor Processing Agent
Monitors input folder, processes new files, archives completed work
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from agents.monitoring.folder_monitor import FolderMonitor
from agents.parsing.pdf_parser import PDFParser
from agents.classification.doc_type_classifier import DocumentTypeClassifier
from agents.classification.relevance_classifier import RelevanceClassifier

# Directory Configuration
INPUT_FOLDER = Path(r"C:\Users\phi3t\12.20 dash\1.5.2026\PDF HTML TRAINING PHI ADD IN")
OUTPUT_FOLDER = BASE_DIR / "output" / "processed_documents"
ARCHIVE_FOLDER = BASE_DIR / "output" / "archive"
PROCESSED_LOG = BASE_DIR / "output" / "logs" / "processed_files.json"

# Processing subdirectories
PARSED_DIR = OUTPUT_FOLDER / "parsed"
CLASSIFIED_DIR = OUTPUT_FOLDER / "classified"
RESULTS_DIR = OUTPUT_FOLDER / "results"

# Create all directories
for dir_path in [OUTPUT_FOLDER, ARCHIVE_FOLDER, PARSED_DIR, CLASSIFIED_DIR, RESULTS_DIR, PROCESSED_LOG.parent]:
    dir_path.mkdir(parents=True, exist_ok=True)


def parse_html(html_path: Path) -> Dict[str, Any]:
    """Parse HTML file to extract text"""
    try:
        from bs4 import BeautifulSoup
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            return {
                "full_text": text,
                "pages": [{"page": 1, "text": text, "char_count": len(text)}],
                "total_char_count": len(text),
                "page_count": 1
            }
    except ImportError:
        # Fallback: read as text
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            return {
                "full_text": text,
                "pages": [{"page": 1, "text": text, "char_count": len(text)}],
                "total_char_count": len(text),
                "page_count": 1
            }


def process_file(file_path: Path, monitor: FolderMonitor) -> Dict[str, Any]:
    """
    Process a single file through the pipeline
    
    Args:
        file_path: File to process
        monitor: Folder monitor instance
        
    Returns:
        Processing result dict
    """
    print(f"\n{'='*70}")
    print(f"Processing: {file_path.name}")
    print(f"{'='*70}")
    
    # Check if already processed
    if monitor.is_already_processed(file_path):
        processed_info = monitor.get_processed_info(file_path)
        print(f"[SKIP] File already processed on {processed_info.get('processed_at', 'unknown')}")
        print(f"       Document ID: {processed_info.get('document_id', 'unknown')}")
        return {
            "status": "already_processed",
            "file_path": str(file_path),
            "processed_info": processed_info
        }
    
    # Generate document ID
    file_hash = monitor.compute_file_hash(file_path)
    document_id = f"doc_{file_path.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    result = {
        "document_id": document_id,
        "filename": file_path.name,
        "file_path": str(file_path),
        "file_type": file_path.suffix.lower(),
        "file_hash": file_hash,
        "file_size": file_path.stat().st_size,
        "processing_started": datetime.utcnow().isoformat(),
        "output_files": [],
        "classifications": {}
    }
    
    try:
        # Step 1: Parse document
        print(f"\n[1/3] Parsing {file_path.suffix.upper()}...")
        if file_path.suffix.lower() == ".pdf":
            parser = PDFParser(PARSED_DIR)
            parse_result = parser.parse(file_path, document_id)
            parsed_text_file = PARSED_DIR / f"{document_id}_parsed_text.json"
            if parsed_text_file.exists():
                with open(parsed_text_file, "r", encoding="utf-8") as f:
                    parsed_text = json.load(f)
            else:
                raise FileNotFoundError("Parsed text file not created")
            result["output_files"].append(str(parsed_text_file))
        else:  # HTML
            parsed_text = parse_html(file_path)
            parsed_text_file = PARSED_DIR / f"{document_id}_parsed_text.json"
            with open(parsed_text_file, "w", encoding="utf-8") as f:
                json.dump(parsed_text, f, indent=2, ensure_ascii=False)
            result["output_files"].append(str(parsed_text_file))
        
        print(f"  [OK] Extracted {parsed_text.get('total_char_count', 0):,} characters")
        
        # Step 2: Classify document type and relevance
        print(f"\n[2/3] Classifying document...")
        doc_classifier = DocumentTypeClassifier()
        doc_type_result = doc_classifier.classify(parsed_text, file_path.name)
        result["classifications"]["document_type"] = doc_type_result
        
        relevance_classifier = RelevanceClassifier()
        relevance_result = relevance_classifier.classify(
            parsed_text,
            file_path.name,
            doc_type_result.get("document_type")
        )
        result["classifications"]["relevance"] = relevance_result
        
        print(f"  [OK] Document type: {doc_type_result.get('document_type')}")
        print(f"  [OK] Relevance: {relevance_result.get('relevance').upper()}")
        print(f"  [OK] Confidence: {relevance_result.get('confidence')}")
        
        if relevance_result.get("is_irrelevant"):
            print(f"  [WARNING] Document is IRRELEVANT to business goals")
            if relevance_result.get("irrelevance_reasons"):
                for reason in relevance_result.get("irrelevance_reasons", []):
                    print(f"     - {reason}")
        
        # Step 3: Save classification results
        print(f"\n[3/3] Saving results...")
        classification_file = CLASSIFIED_DIR / f"{document_id}_classification.json"
        with open(classification_file, "w") as f:
            json.dump(result["classifications"], f, indent=2)
        result["output_files"].append(str(classification_file))
        
        # Save complete result
        result_file = RESULTS_DIR / f"{document_id}_result.json"
        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)
        result["output_files"].append(str(result_file))
        
        result["processing_completed"] = datetime.utcnow().isoformat()
        result["status"] = "success"
        
        # Mark as processed and archive
        monitor.mark_as_processed(
            file_path,
            document_id,
            [Path(f) for f in result["output_files"]],
            {
                "document_type": doc_type_result.get("document_type"),
                "relevance": relevance_result.get("relevance"),
                "is_irrelevant": relevance_result.get("is_irrelevant")
            }
        )
        
        print(f"  [OK] Results saved")
        print(f"  [OK] File archived")
        print(f"  [OK] Marked as processed (won't repeat)")
        
        return result
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        result["status"] = "error"
        result["error"] = str(e)
        result["processing_completed"] = datetime.utcnow().isoformat()
        return result


def main():
    """Main processing loop"""
    print("=" * 70)
    print("Folder Monitor Agent - Document Processing")
    print("=" * 70)
    print(f"Input Folder: {INPUT_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    print(f"Archive Folder: {ARCHIVE_FOLDER}")
    print(f"Processed Log: {PROCESSED_LOG}")
    print(f"Started: {datetime.utcnow().isoformat()}")
    print("=" * 70)
    
    # Initialize folder monitor
    monitor = FolderMonitor(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        archive_folder=ARCHIVE_FOLDER,
        processed_log_file=PROCESSED_LOG
    )
    
    # Get status
    status = monitor.get_processing_status()
    print(f"\nStatus:")
    print(f"  Total processed: {status['total_processed']}")
    print(f"  New files pending: {status['new_files_pending']}")
    
    if status['new_files_pending'] == 0:
        print("\n[OK] No new files to process. All files have been processed.")
        return
    
    print(f"\nNew files to process:")
    for filename in status['new_files']:
        print(f"  - {filename}")
    
    # Process each new file
    new_files = monitor.get_new_files()
    processing_summary = {
        "processing_session": datetime.utcnow().isoformat(),
        "input_folder": str(INPUT_FOLDER),
        "files_processed": [],
        "summary": {
            "total": len(new_files),
            "successful": 0,
            "already_processed": 0,
            "errors": 0
        }
    }
    
    for file_path in new_files:
        result = process_file(file_path, monitor)
        processing_summary["files_processed"].append(result)
        
        if result["status"] == "success":
            processing_summary["summary"]["successful"] += 1
        elif result["status"] == "already_processed":
            processing_summary["summary"]["already_processed"] += 1
        else:
            processing_summary["summary"]["errors"] += 1
    
    # Save processing summary
    summary_file = OUTPUT_FOLDER / f"processing_session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w") as f:
        json.dump(processing_summary, f, indent=2)
    
    # Generate markdown summary
    generate_session_summary(processing_summary, OUTPUT_FOLDER / "PROCESSING_SESSION_SUMMARY.md")
    
    print("\n" + "=" * 70)
    print("Processing Complete!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Total files: {processing_summary['summary']['total']}")
    print(f"  Successfully processed: {processing_summary['summary']['successful']}")
    print(f"  Already processed: {processing_summary['summary']['already_processed']}")
    print(f"  Errors: {processing_summary['summary']['errors']}")
    print(f"\nResults saved to: {OUTPUT_FOLDER}")
    print("=" * 70)


def generate_session_summary(processing_summary: Dict[str, Any], output_file: Path):
    """Generate markdown summary of processing session"""
    
    md_content = f"""# Processing Session Summary

**Session Date:** {processing_summary['processing_session']}  
**Input Folder:** `{processing_summary['input_folder']}`

## Summary

| Metric | Count |
|--------|-------|
| **Total Files** | {processing_summary['summary']['total']} |
| **Successfully Processed** | {processing_summary['summary']['successful']} |
| **Already Processed** | {processing_summary['summary']['already_processed']} |
| **Errors** | {processing_summary['summary']['errors']} |

## Files Processed

"""
    
    for file_result in processing_summary["files_processed"]:
        status_emoji = "[OK]" if file_result["status"] == "success" else "[SKIP]" if file_result["status"] == "already_processed" else "[ERROR]"
        md_content += f"### {status_emoji} {file_result.get('filename', 'Unknown')}\n\n"
        md_content += f"- **Status:** {file_result.get('status', 'unknown')}\n"
        
        if file_result.get("status") == "success":
            md_content += f"- **Document ID:** {file_result.get('document_id')}\n"
            classifications = file_result.get("classifications", {})
            if "document_type" in classifications:
                md_content += f"- **Document Type:** {classifications['document_type'].get('document_type', 'unknown')}\n"
            if "relevance" in classifications:
                rel = classifications["relevance"]
                md_content += f"- **Relevance:** {rel.get('relevance', 'unknown').upper()}\n"
                md_content += f"- **Confidence:** {rel.get('confidence', 0)}\n"
                if rel.get("is_irrelevant"):
                    md_content += f"- **[WARNING] IRRELEVANT** - Not related to business goals\n"
        elif file_result.get("status") == "already_processed":
            info = file_result.get("processed_info", {})
            md_content += f"- **Previously processed:** {info.get('processed_at', 'unknown')}\n"
            md_content += f"- **Document ID:** {info.get('document_id', 'unknown')}\n"
        else:
            md_content += f"- **Error:** {file_result.get('error', 'Unknown error')}\n"
        
        md_content += "\n"
    
    md_content += f"""
## Directory Structure

All outputs are organized in:

```
output/
├── processed_documents/
│   ├── parsed/          # Parsed text, layout, tables
│   ├── classified/      # Classification results
│   └── results/         # Complete processing results
├── archive/             # Archived original files
└── logs/
    └── processed_files.json  # Processing log (prevents duplicates)
```

## How It Works

1. **Monitor Input Folder:** Agent checks for new PDF/HTML files
2. **Check Archive:** Verifies file hasn't been processed (by hash/filename)
3. **Process:** Parses, classifies, and analyzes document
4. **Archive:** Saves original file and marks as processed
5. **Output:** Saves all results to organized directories

## Avoiding Duplicate Work

The system tracks processed files by:
- **File Hash (SHA256):** Unique identifier for file content
- **Filename + Size:** Secondary check
- **Archive Log:** JSON file tracking all processed files

Once a file is processed, it won't be processed again even if:
- File is moved and re-added
- Processing script is run multiple times
- File is renamed (hash check still works)

---
*Generated: {datetime.utcnow().isoformat()}*
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)


if __name__ == "__main__":
    main()
