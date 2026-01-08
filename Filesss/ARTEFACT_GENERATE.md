# Artifact Generation Guide

**Purpose:** How to generate and regenerate the artifact index viewer

---

## Quick Start: Regenerate Artifact Index

### Method 1: Run the Script

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
python scripts/temporal__generate_artifact_index.py
```

**What it does:**
1. Scans `artifacts/` directory for all JSON, MD, TXT, MMD files
2. Organizes artifacts by category (intelligence, drafting, execution, learning, policy, system, other)
3. Reads `_meta` blocks from JSON artifacts
4. Generates `artifacts/ARTIFACT_INDEX.html` (interactive viewer)
5. Generates `artifacts/ARTIFACT_INDEX.json` (machine-readable index)

---

## When to Regenerate

**Regenerate when:**
- ✅ New artifacts are created by agents
- ✅ Artifacts are deleted or moved
- ✅ Artifact metadata (`_meta` blocks) change
- ✅ Artifact counts seem wrong
- ✅ Viewer shows 0 artifacts (fixes embedded data)

**You DON'T need to regenerate:**
- ❌ Just viewing artifacts (viewer reads from API when server is running)
- ❌ Reviewing artifacts (reviews are stored separately)
- ❌ Server is running (viewer loads live data from API)

---

## What Gets Generated

### 1. ARTIFACT_INDEX.html

**Location:** `artifacts/ARTIFACT_INDEX.html`

**Contains:**
- Embedded artifact data (JSON object in JavaScript)
- Interactive viewer UI (HTML/CSS/JavaScript)
- Search and filter functionality
- Review controls (approve/reject/revise buttons)
- Server connection logic

**Size:** Large file (~3000+ lines) with all artifact metadata embedded

### 2. ARTIFACT_INDEX.json

**Location:** `artifacts/ARTIFACT_INDEX.json` (if generated)

**Contains:**
- Machine-readable artifact catalog
- Same structure as embedded data in HTML
- Useful for scripts/tools that need artifact list

---

## How Artifacts Are Organized

### Categories (Based on Directory Names)

- **Intelligence** (`intel_*` directories)
  - Signal scans
  - Stakeholder maps
  - Opposition detection
  - Risk assessments

- **Drafting** (`draft_*` directories)
  - Concept memos
  - Framing documents
  - Whitepapers
  - Legislative language

- **Execution** (`execution_*` directories)
  - Outreach plans
  - Execution logs
  - Campaign strategies

- **Learning** (`learning_*` directories)
  - Outcome analysis
  - Performance reviews
  - Improvement recommendations

- **Policy** (`policy/` directory)
  - Policy documents
  - Strategic plans
  - Diagrams

- **System** (system status, templates, development files)

- **Other** (everything else)

---

## File Structure Scanning

The script scans:

```
artifacts/
├── *.json, *.md, *.txt, *.mmd (root level files)
├── intel_*/ (intelligence artifacts)
├── draft_*/ (drafting artifacts)
├── execution_*/ (execution artifacts)
├── learning_*/ (learning artifacts)
├── policy/ (policy artifacts)
└── [other directories]
```

**Excluded:**
- `.git/` directories
- `rendered/` directory
- `codex_reviews/` directory
- `debug_dashboard/` directory
- `ARTIFACT_INDEX.html` and `ARTIFACT_INDEX.json` (to avoid recursion)

---

## Artifact Metadata

For JSON artifacts, the script reads the `_meta` block:

```json
{
  "_meta": {
    "agent_id": "draft_concept_memo_pre_evt",
    "generated_at": "2026-01-20T12:00:00Z",
    "artifact_type": "PRE_CONCEPT",
    "artifact_name": "Concept Memo",
    "status": "SPECULATIVE",
    "confidence": "SPECULATIVE",
    "human_review_required": true,
    "requires_review": "HR_PRE",
    "guidance_status": "SIGNED"
  },
  ...
}
```

**Extracted fields:**
- `artifact_type` - Used for categorization
- `artifact_name` - Display name
- `status` - SPECULATIVE or ACTIONABLE
- `requires_review` - Review gate ID

---

## Troubleshooting

### "0 artifacts" after regeneration

**Check:**
1. Artifacts directory exists: `agent-orchestrator/artifacts/`
2. Artifacts exist: Look for `.json` or `.md` files in subdirectories
3. Script runs without errors
4. Output file is created: `artifacts/ARTIFACT_INDEX.html`

**Fix:**
```powershell
# Verify artifacts exist
cd agent-orchestrator
dir artifacts\*.json /s /b | measure-object  # Count JSON files

# Regenerate
python scripts/temporal__generate_artifact_index.py
```

### Viewer still shows 0 after regeneration

**Cause:** Viewer might be loading from API instead of embedded data

**Fix:**
1. Check server is running (if it is, viewer uses API data)
2. Stop server, refresh browser (viewer uses embedded data)
3. Or fix the API endpoint (see troubleshooting guide)

### Script errors or fails

**Common errors:**
- `FileNotFoundError` - Check `artifacts/` directory exists
- `PermissionError` - Close viewer HTML file, try again
- `JSONDecodeError` - Some artifact JSON is corrupted (script skips it with warning)

---

## Regeneration Process Flow

```
1. Script starts
   ↓
2. Scan artifacts/ directory
   ├─ Root level files → "other" category
   └─ Subdirectories → Categorized by prefix
      ↓
3. Read each artifact file
   ├─ JSON files → Extract _meta block
   ├─ MD/TXT files → Basic metadata
   └─ Collect file stats (size, modified date)
      ↓
4. Build artifacts_data object
   {
     intelligence: [...],
     drafting: [...],
     execution: [...],
     ...
   }
      ↓
5. Generate HTML viewer
   ├─ Embed artifacts_data as JavaScript
   ├─ Include viewer UI code
   └─ Add initialization logic
      ↓
6. Write ARTIFACT_INDEX.html
   └─ Write ARTIFACT_INDEX.json (if enabled)
```

---

## Integration with Server

### Two Ways to View Artifacts

**1. Static (Embedded Data):**
- Open `ARTIFACT_INDEX.html` directly (double-click)
- Uses embedded artifact data
- Works offline
- Needs regeneration when artifacts change

**2. Live (API Data):**
- Start review server: `START_REVIEW_SERVER.bat`
- Open `http://localhost:8080`
- Loads artifacts from `/api/v1/artifacts/index`
- Always up-to-date (no regeneration needed)
- Requires server running

**Best Practice:**
- Regenerate index when creating new artifacts
- Use server for daily review (live data)
- Embedded data is fallback when server offline

---

## Script Details

**File:** `scripts/temporal__generate_artifact_index.py`

**Dependencies:**
- Python 3.8+
- Standard library only (json, pathlib, datetime)

**Runtime:**
- Fast: Scans ~100 artifacts in < 1 second
- Safe: Skips corrupted files with warnings
- Idempotent: Can run multiple times safely

**Output:**
- Overwrites `ARTIFACT_INDEX.html` (backup manually if needed)
- Creates new file each time (no append mode)

---

## Manual Regeneration Steps

```powershell
# 1. Navigate to project
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"

# 2. Run generation script
python scripts/temporal__generate_artifact_index.py

# 3. Verify output
dir artifacts\ARTIFACT_INDEX.html

# 4. Open viewer
start artifacts\ARTIFACT_INDEX.html
```

---

## Summary

**To regenerate artifact index:**
```powershell
python scripts/temporal__generate_artifact_index.py
```

**When to regenerate:**
- After creating new artifacts
- If viewer shows wrong counts
- When artifacts are moved/deleted

**The batch file:** There isn't one specifically for regeneration, but you can create one or just run the Python script directly.
