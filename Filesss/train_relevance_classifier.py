"""
Train relevance classifier on training documents
Processes PDFs/HTMLs and learns to identify irrelevant documents
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from agents.parsing.pdf_parser import PDFParser
from agents.classification.relevance_classifier import RelevanceClassifier
from agents.classification.doc_type_classifier import DocumentTypeClassifier

# Training directory
TRAINING_DIR = Path(r"C:\Users\phi3t\12.20 dash\1.5.2026\PDF HTML TRAINING PHI ADD IN")

# Output directory
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PARSED_DIR = OUTPUT_DIR / "parsed"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_DIR = OUTPUT_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


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


def main():
    """Train relevance classifier on training documents"""
    
    print("=" * 70)
    print("Relevance Classifier Training")
    print("=" * 70)
    print(f"Training directory: {TRAINING_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Started: {datetime.utcnow().isoformat()}")
    print("-" * 70)
    
    # Initialize components
    pdf_parser = PDFParser(PARSED_DIR)
    doc_classifier = DocumentTypeClassifier()
    relevance_classifier = RelevanceClassifier()
    
    training_results = {
        "training_started": datetime.utcnow().isoformat(),
        "training_directory": str(TRAINING_DIR),
        "documents_processed": [],
        "summary": {
            "total_documents": 0,
            "relevant": 0,
            "irrelevant": 0,
            "uncertain": 0
        }
    }
    
    # Find all PDF and HTML files
    pdf_files = list(TRAINING_DIR.glob("*.pdf"))
    html_files = list(TRAINING_DIR.glob("*.html"))
    all_files = pdf_files + html_files
    
    print(f"\nFound {len(all_files)} documents to process:")
    for f in all_files:
        print(f"  - {f.name}")
    
    print("\n" + "=" * 70)
    
    # Process each document
    for idx, file_path in enumerate(all_files, 1):
        print(f"\n[{idx}/{len(all_files)}] Processing: {file_path.name}")
        print("-" * 70)
        
        document_id = f"doc_{file_path.stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        doc_result = {
            "filename": file_path.name,
            "file_path": str(file_path),
            "file_type": file_path.suffix.lower(),
            "document_id": document_id
        }
        
        try:
            # Parse document
            if file_path.suffix.lower() == ".pdf":
                print("  Parsing PDF...")
                parse_result = pdf_parser.parse(file_path, document_id)
                parsed_text_file = PARSED_DIR / f"{document_id}_parsed_text.json"
                if parsed_text_file.exists():
                    with open(parsed_text_file, "r", encoding="utf-8") as f:
                        parsed_text = json.load(f)
                else:
                    print("  ⚠ Parsed text file not found")
                    continue
            else:  # HTML
                print("  Parsing HTML...")
                parsed_text = parse_html(file_path)
                # Save parsed text
                parsed_text_file = PARSED_DIR / f"{document_id}_parsed_text.json"
                with open(parsed_text_file, "w", encoding="utf-8") as f:
                    json.dump(parsed_text, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Extracted {parsed_text.get('total_char_count', 0):,} characters")
            
            # Classify document type
            print("  Classifying document type...")
            doc_type_result = doc_classifier.classify(parsed_text, file_path.name)
            doc_result["document_type"] = doc_type_result.get("document_type")
            doc_result["document_type_confidence"] = doc_type_result.get("confidence")
            print(f"  ✓ Document type: {doc_result['document_type']} (confidence: {doc_result['document_type_confidence']})")
            
            # Classify relevance
            print("  Classifying relevance...")
            relevance_result = relevance_classifier.classify(
                parsed_text,
                file_path.name,
                doc_result["document_type"]
            )
            doc_result["relevance"] = relevance_result.get("relevance")
            doc_result["relevance_confidence"] = relevance_result.get("confidence")
            doc_result["is_irrelevant"] = relevance_result.get("is_irrelevant")
            doc_result["relevance_score"] = relevance_result.get("relevance_score")
            doc_result["irrelevance_reasons"] = relevance_result.get("irrelevance_reasons", [])
            doc_result["relevant_keywords"] = relevance_result.get("relevant_keywords_found", [])
            doc_result["irrelevant_keywords"] = relevance_result.get("irrelevant_keywords_found", [])
            
            # Update summary
            training_results["summary"]["total_documents"] += 1
            if doc_result["relevance"] == "relevant":
                training_results["summary"]["relevant"] += 1
            elif doc_result["relevance"] == "irrelevant":
                training_results["summary"]["irrelevant"] += 1
            else:
                training_results["summary"]["uncertain"] += 1
            
            print(f"  ✓ Relevance: {doc_result['relevance'].upper()}")
            print(f"    Confidence: {doc_result['relevance_confidence']}")
            print(f"    Score: {doc_result['relevance_score']}")
            if doc_result["irrelevance_reasons"]:
                print(f"    Reasons: {', '.join(doc_result['irrelevance_reasons'])}")
            
            # Learn from this example if it's clearly irrelevant
            if doc_result["is_irrelevant"]:
                print("  📚 Learning from irrelevant example...")
                reason = "; ".join(doc_result["irrelevance_reasons"])
                relevance_classifier.learn_from_example(
                    parsed_text,
                    file_path.name,
                    is_irrelevant=True,
                    reason=reason
                )
                print("  ✓ Updated classifier patterns")
            
            # Save individual result
            result_file = PROCESSED_DIR / f"{document_id}_relevance.json"
            with open(result_file, "w") as f:
                json.dump(doc_result, f, indent=2)
            doc_result["result_file"] = str(result_file)
            
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")
            doc_result["error"] = str(e)
            doc_result["status"] = "error"
        
        training_results["documents_processed"].append(doc_result)
    
    # Finalize training
    training_results["training_completed"] = datetime.utcnow().isoformat()
    training_results["classifier_patterns"] = {
        "irrelevance_patterns": relevance_classifier.irrelevance_patterns,
        "irrelevant_keywords": relevance_classifier.BUSINESS_KEYWORDS["irrelevant"]
    }
    
    # Save training results
    results_file = OUTPUT_DIR / "relevance_training_results.json"
    with open(results_file, "w") as f:
        json.dump(training_results, f, indent=2)
    
    # Generate summary markdown
    summary_file = OUTPUT_DIR / "RELEVANCE_TRAINING_SUMMARY.md"
    generate_summary_markdown(training_results, summary_file)
    
    print("\n" + "=" * 70)
    print("Training Complete!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Total documents: {training_results['summary']['total_documents']}")
    print(f"  Relevant: {training_results['summary']['relevant']}")
    print(f"  Irrelevant: {training_results['summary']['irrelevant']}")
    print(f"  Uncertain: {training_results['summary']['uncertain']}")
    print(f"\nResults saved to:")
    print(f"  - {results_file}")
    print(f"  - {summary_file}")
    print("=" * 70)
    
    return training_results


def generate_summary_markdown(training_results: Dict[str, Any], output_file: Path):
    """Generate markdown summary of training results"""
    
    md_content = f"""# Relevance Classifier Training Summary

## Training Overview

**Training Date:** {training_results['training_started']}  
**Training Directory:** `{training_results['training_directory']}`  
**Total Documents Processed:** {training_results['summary']['total_documents']}

## Results Summary

| Category | Count | Percentage |
|----------|-------|------------|
| **Relevant** | {training_results['summary']['relevant']} | {(training_results['summary']['relevant'] / max(training_results['summary']['total_documents'], 1) * 100):.1f}% |
| **Irrelevant** | {training_results['summary']['irrelevant']} | {(training_results['summary']['irrelevant'] / max(training_results['summary']['total_documents'], 1) * 100):.1f}% |
| **Uncertain** | {training_results['summary']['uncertain']} | {(training_results['summary']['uncertain'] / max(training_results['summary']['total_documents'], 1) * 100):.1f}% |

## Documents Processed

"""
    
    for doc in training_results["documents_processed"]:
        status_emoji = "❌" if doc.get("is_irrelevant") else "✅" if doc.get("relevance") == "relevant" else "❓"
        md_content += f"### {status_emoji} {doc.get('filename', 'Unknown')}\n\n"
        md_content += f"- **File Type:** {doc.get('file_type', 'unknown')}\n"
        md_content += f"- **Document Type:** {doc.get('document_type', 'unknown')} (confidence: {doc.get('document_type_confidence', 0)})\n"
        md_content += f"- **Relevance:** {doc.get('relevance', 'unknown').upper()}\n"
        md_content += f"- **Confidence:** {doc.get('relevance_confidence', 0)}\n"
        md_content += f"- **Relevance Score:** {doc.get('relevance_score', 0)}\n"
        
        if doc.get("irrelevance_reasons"):
            md_content += f"- **Irrelevance Reasons:**\n"
            for reason in doc.get("irrelevance_reasons", []):
                md_content += f"  - {reason}\n"
        
        if doc.get("relevant_keywords"):
            md_content += f"- **Relevant Keywords Found:** {', '.join(doc.get('relevant_keywords', [])[:5])}\n"
        
        if doc.get("irrelevant_keywords"):
            md_content += f"- **Irrelevant Keywords Found:** {', '.join(doc.get('irrelevant_keywords', [])[:5])}\n"
        
        if doc.get("error"):
            md_content += f"- **Error:** {doc.get('error')}\n"
        
        md_content += "\n"
    
    md_content += f"""## Classifier Patterns Learned

### Irrelevance Patterns
"""
    for pattern in training_results.get("classifier_patterns", {}).get("irrelevance_patterns", []):
        md_content += f"- `{pattern}`\n"
    
    md_content += f"\n### Irrelevant Keywords\n"
    for keyword in training_results.get("classifier_patterns", {}).get("irrelevant_keywords", []):
        md_content += f"- {keyword}\n"
    
    md_content += f"""
## Models Used

- **PDF Parser:** pdfplumber/PyMuPDF (text extraction, layout, tables)
- **Document Type Classifier:** Rule-based keyword matching
- **Relevance Classifier:** Pattern matching + keyword analysis

## Output Files

All processed documents and results are saved in the `output/` directory:

- `output/parsed/` - Parsed text, layout, and tables
- `output/processed/` - Individual document relevance classifications
- `output/relevance_training_results.json` - Complete training results (JSON)
- `output/RELEVANCE_TRAINING_SUMMARY.md` - This summary file

## Business Goal Context

The classifier is trained to identify documents relevant to **Investment Sales Business Development**, specifically:

- Real estate transactions
- Property ownership and management
- Commercial real estate investments
- Debt and financing
- Lease and occupancy data
- Market analysis and valuations

Documents that are **NOT relevant** include:
- Congressional bills and legislation
- Government policy documents
- Unrelated industry content
- Non-real-estate topics

## Next Steps

1. Review the classifications for accuracy
2. Add more training examples to improve classifier
3. Fine-tune patterns and keywords based on results
4. Integrate relevance classifier into main pipeline to filter irrelevant documents early

---
*Generated: {datetime.utcnow().isoformat()}*
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"\n✓ Summary markdown saved to: {output_file}")


if __name__ == "__main__":
    results = main()
