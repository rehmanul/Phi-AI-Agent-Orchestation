# Artifact Viewer - Access Pathways

**Generated:** 2026-01-07  
**Total Artifacts:** 96 artifacts across 7 categories

---

## 🚀 Quick Access

### Method 1: Open HTML Viewer Directly

**Path:**
```
C:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\artifacts\ARTIFACT_INDEX.html
```

**How to Open:**
1. Navigate to: `agent-orchestrator/artifacts/`
2. Double-click: `ARTIFACT_INDEX.html`
3. Or right-click → "Open with" → Your browser

### Method 2: Use Launch Script

**Path:**
```
C:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\artifacts\OPEN_ARTIFACT_VIEWER.bat
```

**How to Run:**
1. Navigate to: `agent-orchestrator/artifacts/`
2. Double-click: `OPEN_ARTIFACT_VIEWER.bat`
3. Viewer opens in your default browser

### Method 3: Open from Command Line

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\artifacts"
start ARTIFACT_INDEX.html
```

Or:
```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\artifacts"
.\OPEN_ARTIFACT_VIEWER.bat
```

---

## 📊 What You'll See

### Interactive Viewer Features

- **Tabs:** Browse by category (Intelligence, Drafting, Execution, Learning, Policy, System, All)
- **Search:** Filter artifacts by name, path, or type
- **Statistics:** See counts per category
- **Artifact Cards:** Each artifact shows:
  - Name and path
  - Directory location
  - File size and modification date
  - Status (SPECULATIVE/ACTIONABLE)
  - Open File button (direct file access)

### Artifact Categories

1. **🔍 Intelligence** (8 artifacts)
   - Signal scans
   - Stakeholder maps
   - Opposition detection
   - Policy context analysis

2. **✍️ Drafting** (8 artifacts)
   - Concept memos
   - Policy framing
   - Whitepapers
   - Committee briefings
   - Legislative language
   - Amendment strategies

3. **⚙️ Execution** (2 artifacts)
   - Outreach execution plans
   - Execution logs

4. **📐 Learning** (2 artifacts)
   - Outcome analysis
   - Tactic performance

5. **📋 Policy** (29 artifacts)
   - Policy documents
   - Stakeholder maps
   - Action plans
   - Talking points
   - Diagrams

6. **🔧 System** (5 artifacts)
   - System status snapshots
   - Review templates
   - Development tools

7. **Other** (42 artifacts)
   - Hypothetical artifacts
   - Scenario analyses
   - Core planner outputs
   - Mermaid diagrams

---

## 📁 Key Artifact Locations

### Most Important Artifacts (COMM_EVT Phase)

**Drafting Artifacts:**
- `artifacts/draft_committee_briefing_comm_evt/committee_briefing_packet.json`
- `artifacts/draft_legislative_language_comm_evt/COMM_LEGISLATIVE_LANGUAGE.json`
- `artifacts/draft_amendment_strategy_comm_evt/COMM_AMENDMENT_STRATEGY.json`

**Execution Artifacts:**
- `artifacts/execution_outreach_comm_evt/outreach_execution_plan.json`

**Intelligence Artifacts:**
- `artifacts/intel_stakeholder_map_comm_evt/stakeholder_map.json`
- `artifacts/intel_policy_context_analyzer_pre_evt/POLICY_CONTEXT_ANALYSIS.json`

---

## 🔄 Regenerate Index

To update the index after new artifacts are created:

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
python scripts/temporal__generate_artifact_index.py
```

This will:
1. Scan all artifacts in `artifacts/` directory
2. Update `ARTIFACT_INDEX.json`
3. Regenerate `ARTIFACT_INDEX.html` viewer

---

## 📝 Notes

- **JSON Index:** Machine-readable format at `artifacts/ARTIFACT_INDEX.json`
- **HTML Viewer:** Interactive browser-based viewer at `artifacts/ARTIFACT_INDEX.html`
- **File Paths:** All paths in viewer use forward slashes (`/`) but work on Windows
- **Open File Button:** Uses `file:///` protocol - may require browser permission

---

**Quick Start:** Just double-click `OPEN_ARTIFACT_VIEWER.bat` in the artifacts folder!
