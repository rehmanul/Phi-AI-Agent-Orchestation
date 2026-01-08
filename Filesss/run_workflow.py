"""
Execution script for Agentic Coding Development Workflow

Runs the workflow and displays outputs
"""

import sys
from pathlib import Path
from workflow_engine import WorkflowEngine
import json


def print_output_file(file_path: Path):
    """Display contents of an output file"""
    if not file_path.exists():
        print(f"   [WARN] File not found: {file_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"[FILE] {file_path.name}")
    print(f"{'='*60}")
    
    if file_path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(json.dumps(data, indent=2))
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f.read())
    
    print(f"{'='*60}\n")


def main():
    """Main execution function"""
    # Initialize workflow engine
    engine = WorkflowEngine(output_dir="output")
    
    # Example task
    task_description = "Create a Python function to process user input with validation and error handling"
    
    # Run workflow
    results = engine.run_workflow(task_description)
    
    # Display outputs
    print("\n" + "="*60)
    print("[OUTPUTS] VIEWABLE OUTPUTS")
    print("="*60)
    
    if results.get("summary"):
        summary_path = Path(results["summary"])
        print(f"\n[SUMMARY] Workflow Summary: {summary_path}")
        print_output_file(summary_path)
    
    # Display each output file
    output_files = results.get("outputs", {})
    for output_name, file_path in output_files.items():
        print(f"\n[FILE] {output_name.replace('_', ' ').title()}: {file_path}")
        print_output_file(Path(file_path))
    
    print("\n" + "="*60)
    print("[DONE] Workflow execution complete!")
    print(f"[LOCATION] All outputs saved in: {Path(results.get('summary', '')).parent}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
