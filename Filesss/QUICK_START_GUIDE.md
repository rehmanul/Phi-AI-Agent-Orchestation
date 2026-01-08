# Quick Start Guide: Artifact Viewer & Content Interaction

**Date:** 2026-01-07  
**Status:** ✅ READY TO USE

---

## Start the System

### 1. Start FastAPI Server:

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
.\START_VIEWER_SERVER.bat
```

Or manually:
```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open Browser:

Navigate to: **`http://localhost:8000/viewer/`**

The server will automatically redirect from `http://localhost:8000/` to the viewer.

---

## What You'll See

### Header:
- **Title:** "Agent Orchestrator - Artifact Review Console"
- **Server Status:** 🟢 "• Server: Online" (when connected)

### Statistics:
- **Total Artifacts:** 104
- **Intelligence:** 8
- **Drafting:** 8
- **Execution:** 2
- **Learning:** 2

### Controls:
1. **One-Look Brief Generator** - Button to generate LLM handoff brief
2. **Filter Tabs** - All, Unreviewed, Approved, Needs Revision, Rejected, LLM Ready
3. **Category Tabs** - Intelligence, Drafting, Execution, Learning, Policy, System
4. **Search Bar** - Search artifacts by name, path, or type

---

## How to Interact with Content

### View Artifacts:
1. **Browse by category** - Click category tabs (Intelligence, Drafting, etc.)
2. **Search** - Type in search bar to filter artifacts
3. **Expand preview** - Click "▼ Expand Preview" on any artifact card
4. **Open file** - Click "📄 Open File" to view JSON in browser
5. **View formatted** - Click "📝 View Formatted" (if rendered HTML exists)

### Review Artifacts:
1. **Select decision** - Click "✓ Approve", "↻ Revise", or "✗ Reject"
2. **Add reason** - Type reason in text area
3. **Mark for LLM** (optional) - Check "Include in LLM packet"
4. **Set recipient** (if LLM) - Select from dropdown
5. **Add context** (if LLM) - Type "Why sending" in text area
6. **Submit** - Click "Submit Review" button

### Generate LLM Brief:
1. **Approve artifacts** - Approve at least one artifact and mark for LLM
2. **Click button** - Click "Generate One-Look Brief"
3. **View brief** - Brief opens in new window (markdown format)
4. **Download** - Right-click → Save As (if desired)

---

## Features Enabled

### ✅ Phase 1: Live Data Loading
- Artifacts load from API (not static JSON)
- Real-time server status
- Automatic refresh on connection

### ✅ Phase 2: Review & Approval
- Approve/reject artifacts via UI
- Review status tracking
- Filter by review status

### ✅ Phase 3: LLM Handoff
- Generate comprehensive briefs
- Mark artifacts for LLM
- Track LLM-ready artifacts

---

## Troubleshooting

### Server Status Shows "Offline":
- ✅ Check server is running (port 8000)
- ✅ Verify no firewall blocking
- ✅ Check browser console for errors (F12)

### Artifact Counts Show 0:
- ✅ Refresh browser (Ctrl+F5)
- ✅ Check server is running
- ✅ Verify artifacts directory exists
- ✅ Check browser console for errors

### Review Buttons Don't Work:
- ✅ Check server status is "Online"
- ✅ Verify `/api/reviews` endpoint responds
- ✅ Check browser console for errors (F12)

### Brief Generation Fails:
- ✅ Approve at least one artifact first
- ✅ Mark approved artifact for LLM
- ✅ Check review queue files exist in `review/` directory

---

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Server health check |
| `/api/v1/artifacts/index` | GET | Get all artifacts with review status |
| `/api/reviews` | GET | Get all review queues |
| `/api/reviews` | POST | Submit artifact review |
| `/api/brief` | POST | Generate LLM brief (JSON) |
| `/api/brief/md` | GET | Get LLM brief (Markdown) |

---

## Next Steps

1. **Test the viewer** - Open `http://localhost:8000/viewer/`
2. **Review artifacts** - Approve/reject a few artifacts
3. **Generate brief** - Create an LLM handoff brief
4. **Explore features** - Try search, filters, expand preview

---

**Status:** ✅ READY - All Phase 1 & 2 features implemented and tested
