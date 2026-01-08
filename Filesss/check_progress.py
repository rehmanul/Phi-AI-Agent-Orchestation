"""
Quick progress checker - Shows current processing status
"""

import sys
from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from agents.monitoring.folder_monitor import FolderMonitor

# Configuration
INPUT_FOLDER = Path(r"C:\Users\phi3t\12.20 dash\1.5.2026\PDF HTML TRAINING PHI ADD IN")
OUTPUT_FOLDER = BASE_DIR / "output" / "processed_documents"
ARCHIVE_FOLDER = BASE_DIR / "output" / "archive"
PROCESSED_LOG = BASE_DIR / "output" / "logs" / "processed_files.json"

def main():
    """Check and display progress"""
    print("=" * 70)
    print("Progress Check - Folder Monitor System")
    print("=" * 70)
    print(f"Time: {datetime.utcnow().isoformat()}")
    print()
    
    # Initialize monitor
    monitor = FolderMonitor(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        archive_folder=ARCHIVE_FOLDER,
        processed_log_file=PROCESSED_LOG
    )
    
    # Get status
    status = monitor.get_processing_status()
    
    print("INPUT FOLDER:")
    print(f"  Location: {status['input_folder']}")
    
    # Count files in input folder
    pdf_files = list(INPUT_FOLDER.glob("*.pdf"))
    html_files = list(INPUT_FOLDER.glob("*.html"))
    total_input_files = len(pdf_files) + len(html_files)
    
    print(f"  Total files: {total_input_files}")
    print(f"    - PDF files: {len(pdf_files)}")
    print(f"    - HTML files: {len(html_files)}")
    
    print()
    print("PROCESSING STATUS:")
    print(f"  Total processed: {status['total_processed']}")
    print(f"  New files pending: {status['new_files_pending']}")
    
    if total_input_files > 0:
        progress_pct = (status['total_processed'] / total_input_files) * 100
        print(f"  Progress: {progress_pct:.1f}%")
    
    print()
    if status['new_files_pending'] > 0:
        print("NEW FILES TO PROCESS:")
        for filename in status['new_files']:
            print(f"  - {filename}")
    else:
        print("[OK] All files have been processed!")
    
    print()
    print("OUTPUT LOCATIONS:")
    print(f"  Processed documents: {status['output_folder']}")
    print(f"  Archive: {status['archive_folder']}")
    
    # Count output files
    if OUTPUT_FOLDER.exists():
        parsed_count = len(list((OUTPUT_FOLDER / "parsed").glob("*.json"))) if (OUTPUT_FOLDER / "parsed").exists() else 0
        classified_count = len(list((OUTPUT_FOLDER / "classified").glob("*.json"))) if (OUTPUT_FOLDER / "classified").exists() else 0
        results_count = len(list((OUTPUT_FOLDER / "results").glob("*.json"))) if (OUTPUT_FOLDER / "results").exists() else 0
        
        print()
        print("OUTPUT FILE COUNTS:")
        print(f"  Parsed files: {parsed_count}")
        print(f"  Classified files: {classified_count}")
        print(f"  Result files: {results_count}")
    
    # Show recent processing
    if PROCESSED_LOG.exists():
        with open(PROCESSED_LOG, "r") as f:
            processed = json.load(f)
        
        if processed:
            print()
            print("RECENTLY PROCESSED (last 5):")
            recent = list(processed.values())[-5:]
            for file_info in recent:
                print(f"  - {file_info.get('filename')} ({file_info.get('processed_at', 'unknown')})")
                print(f"    Document ID: {file_info.get('document_id', 'unknown')}")
                metadata = file_info.get('processing_metadata', {})
                if metadata:
                    print(f"    Type: {metadata.get('document_type', 'unknown')}, Relevance: {metadata.get('relevance', 'unknown')}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
