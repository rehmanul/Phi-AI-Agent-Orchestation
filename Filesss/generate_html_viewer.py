"""
Generate HTML viewer for workflow outputs
"""

import json
from pathlib import Path
from datetime import datetime
import glob


def find_latest_workflow_output():
    """Find the most recent workflow output directory"""
    output_dir = Path("output")
    if not output_dir.exists():
        return None
    
    workflow_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("workflow_")]
    if not workflow_dirs:
        return None
    
    # Sort by name (which includes timestamp) and get latest
    latest = sorted(workflow_dirs, key=lambda x: x.name, reverse=True)[0]
    return latest


def load_json_file(file_path):
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def load_markdown_file(file_path):
    """Load markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading file: {str(e)}"


def generate_html_viewer(workflow_dir):
    """Generate HTML viewer for workflow outputs"""
    
    # Load all output files
    summary_file = workflow_dir / "workflow_summary.json"
    narrative_file = workflow_dir / "draft_narrative.md"
    differential_file = workflow_dir / "differential_table.json"
    evidence_gaps_file = workflow_dir / "evidence_gaps.json"
    confidence_file = workflow_dir / "confidence_bands.json"
    decision_log_file = workflow_dir / "decision_log.json"
    
    summary = load_json_file(summary_file) if summary_file.exists() else {}
    narrative = load_markdown_file(narrative_file) if narrative_file.exists() else ""
    differential = load_json_file(differential_file) if differential_file.exists() else []
    evidence_gaps = load_json_file(evidence_gaps_file) if evidence_gaps_file.exists() else []
    confidence = load_json_file(confidence_file) if confidence_file.exists() else {}
    decision_log = load_json_file(decision_log_file) if decision_log_file.exists() else []
    
    # Convert markdown to HTML (simple conversion)
    narrative_html = narrative
    narrative_html = narrative_html.replace('## ', '<h3>').replace('##', '</h3>')
    narrative_html = narrative_html.replace('### ', '<h4>').replace('###', '</h4>')
    narrative_html = narrative_html.replace('# ', '<h2>').replace('#', '</h2>')
    # Convert line breaks
    narrative_html = narrative_html.replace('\n\n', '</p><p>')
    narrative_html = '<p>' + narrative_html + '</p>'
    narrative_html = narrative_html.replace('\n- ', '<br>- ')
    narrative_html = narrative_html.replace('</p><p>', '</p><p>')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Coding Workflow - Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .section-header {{
            background: #f5f5f5;
            padding: 15px 20px;
            font-size: 1.3em;
            font-weight: bold;
            border-bottom: 2px solid #667eea;
            color: #333;
        }}
        .section-content {{
            padding: 20px;
            background: white;
        }}
        .workflow-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        .info-card strong {{
            display: block;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .gate-status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }}
        .gate-pass {{
            background: #d4edda;
            color: #155724;
        }}
        .gate-fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        .differential-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .differential-table th,
        .differential-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .differential-table th {{
            background: #667eea;
            color: white;
        }}
        .differential-table tr:hover {{
            background: #f5f5f5;
        }}
        .selected {{
            background: #d4edda !important;
            font-weight: bold;
        }}
        .confidence-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 25px;
            margin: 10px 0;
            overflow: hidden;
        }}
        .confidence-fill {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            padding: 0 10px;
        }}
        .confidence-high {{ background: #28a745; }}
        .confidence-medium {{ background: #ffc107; color: #333; }}
        .confidence-low {{ background: #dc3545; }}
        .evidence-gap {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .narrative-content {{
            line-height: 1.8;
            font-size: 1.1em;
        }}
        .narrative-content h3 {{
            color: #667eea;
            margin: 20px 0 10px 0;
        }}
        .narrative-content h4 {{
            color: #764ba2;
            margin: 15px 0 8px 0;
        }}
        .json-display {{
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .decision-log-item {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agentic Coding Development Workflow</h1>
            <div class="subtitle">Workflow Results Viewer</div>
        </div>
        
        <div class="content">
            <!-- Workflow Summary -->
            <div class="section">
                <div class="section-header">Workflow Summary</div>
                <div class="section-content">
                    <div class="workflow-info">
                        <div class="info-card">
                            <strong>Workflow ID</strong>
                            {summary.get('workflow_id', 'N/A')}
                        </div>
                        <div class="info-card">
                            <strong>Timestamp</strong>
                            {summary.get('timestamp', 'N/A')}
                        </div>
                        <div class="info-card">
                            <strong>Status</strong>
                            <span class="gate-status gate-pass">Completed</span>
                        </div>
                    </div>
                    
                    <h3>Control Gates Status</h3>
                    {generate_gates_html(summary.get('gate_results', {}))}
                </div>
            </div>
            
            <!-- Draft Narrative -->
            <div class="section">
                <div class="section-header">Draft Narrative</div>
                <div class="section-content narrative-content">
                    {narrative_html}
                </div>
            </div>
            
            <!-- Differential Table -->
            <div class="section">
                <div class="section-header">Differential Table - Alternative Approaches</div>
                <div class="section-content">
                    {generate_differential_table(differential)}
                </div>
            </div>
            
            <!-- Confidence Bands -->
            <div class="section">
                <div class="section-header">Confidence Bands</div>
                <div class="section-content">
                    {generate_confidence_html(confidence)}
                </div>
            </div>
            
            <!-- Evidence Gaps -->
            <div class="section">
                <div class="section-header">Evidence Gaps</div>
                <div class="section-content">
                    {generate_evidence_gaps_html(evidence_gaps)}
                </div>
            </div>
            
            <!-- Decision Log -->
            <div class="section">
                <div class="section-header">Decision Log</div>
                <div class="section-content">
                    {generate_decision_log_html(decision_log)}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    output_dir = Path("output")
    html_file = output_dir / "latest_viewer.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[OK] HTML viewer generated: {html_file}")
    return html_file


def generate_gates_html(gates):
    """Generate HTML for control gates"""
    if not gates:
        return "<p>No gate information available</p>"
    
    html = "<div style='margin-top: 15px;'>"
    for gate_name, gate_data in gates.items():
        if gate_name == "can_proceed":
            continue
        status = gate_data.get("status", "unknown")
        status_class = "gate-pass" if status == "pass" else "gate-fail"
        html += f"""
        <div style='margin: 10px 0;'>
            <strong>{gate_name.replace('_', ' ').title()}:</strong>
            <span class='gate-status {status_class}'>{status.upper()}</span>
            <div style='margin-left: 20px; color: #666; font-size: 0.9em;'>
                {gate_data.get('reason', '')}
            </div>
        </div>
        """
    html += "</div>"
    return html


def generate_differential_table(differential):
    """Generate HTML table for differential approaches"""
    if not differential:
        return "<p>No differential data available</p>"
    
    html = "<table class='differential-table'><thead><tr>"
    html += "<th>Approach</th><th>Pros</th><th>Cons</th><th>Selected</th>"
    html += "</tr></thead><tbody>"
    
    for item in differential:
        row_class = "selected" if item.get("selected") else ""
        html += f"<tr class='{row_class}'>"
        html += f"<td><strong>{item.get('approach', 'N/A')}</strong></td>"
        html += f"<td>{', '.join(item.get('pros', []))}</td>"
        html += f"<td>{', '.join(item.get('cons', []))}</td>"
        html += f"<td>{'✓ Selected' if item.get('selected') else ''}</td>"
        html += "</tr>"
    
    html += "</tbody></table>"
    return html


def generate_confidence_html(confidence):
    """Generate HTML for confidence bands"""
    if not confidence:
        return "<p>No confidence data available</p>"
    
    html = "<div>"
    
    # Overall confidence
    overall = confidence.get("overall_confidence", "medium")
    overall_class = f"confidence-{overall}"
    html += f"""
    <div>
        <strong>Overall Confidence:</strong>
        <div class="confidence-bar">
            <div class="confidence-fill {overall_class}" style="width: 100%">
                {overall.upper()}
            </div>
        </div>
    </div>
    """
    
    # Breakdown
    breakdown = confidence.get("confidence_breakdown", {})
    if breakdown:
        html += "<h4 style='margin-top: 25px;'>Confidence Breakdown:</h4>"
        for key, value in breakdown.items():
            value_class = f"confidence-{value}"
            width_map = {"high": "80%", "medium": "50%", "low": "30%"}
            width = width_map.get(value, "50%")
            html += f"""
            <div>
                <strong>{key.replace('_', ' ').title()}:</strong>
                <div class="confidence-bar">
                    <div class="confidence-fill {value_class}" style="width: {width}">
                        {value.upper()}
                    </div>
                </div>
            </div>
            """
    
    html += "</div>"
    return html


def generate_evidence_gaps_html(evidence_gaps):
    """Generate HTML for evidence gaps"""
    if not evidence_gaps:
        return "<p>No evidence gaps identified</p>"
    
    html = ""
    for gap in evidence_gaps:
        html += f'<div class="evidence-gap">{gap}</div>'
    
    return html


def generate_decision_log_html(decision_log):
    """Generate HTML for decision log"""
    if not decision_log:
        return "<p>No decision log entries</p>"
    
    html = ""
    for entry in decision_log:
        html += '<div class="decision-log-item">'
        html += f'<div class="timestamp">Timestamp: {entry.get("timestamp", "N/A")}</div>'
        html += f'<div><strong>Task:</strong> {entry.get("task", "N/A")}</div>'
        html += f'<div><strong>Status:</strong> {entry.get("status", "N/A")}</div>'
        html += '<div class="json-display"><pre>'
        html += json.dumps(entry.get("gate_results", {}), indent=2)
        html += '</pre></div>'
        html += '</div>'
    
    return html


def main():
    """Main function"""
    workflow_dir = find_latest_workflow_output()
    
    if not workflow_dir:
        print("[ERROR] No workflow output found. Please run the workflow first.")
        return
    
    print(f"[INFO] Found workflow output: {workflow_dir}")
    html_file = generate_html_viewer(workflow_dir)
    print(f"[SUCCESS] HTML viewer ready: {html_file}")


if __name__ == "__main__":
    main()
