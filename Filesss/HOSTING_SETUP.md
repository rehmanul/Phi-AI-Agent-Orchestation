# Artifact Viewer Hosting Setup

**Status:** ✅ CONFIGURED  
**Date:** 2026-01-07

---

## Hosting Options

### Option 1: FastAPI Backend (Recommended)

The artifact viewer is now hosted via the FastAPI backend at:

**URL:** `http://localhost:8000/`

**Alternative URL:** `http://localhost:8000/viewer`

**Static Files:** `http://localhost:8000/artifacts/`

#### Start the server:

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:
```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\app"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Access the viewer:

1. Start the FastAPI server (command above)
2. Open browser to: `http://localhost:8000/`
3. Automatically redirects to artifact viewer

#### API endpoints available:

- `http://localhost:8000/` → Artifact viewer (auto-redirect)
- `http://localhost:8000/viewer` → Artifact viewer (direct)
- `http://localhost:8000/artifacts/ARTIFACT_INDEX.html` → Artifact viewer (static)
- `http://localhost:8000/artifacts/ARTIFACT_INDEX.json` → JSON index (API)
- `http://localhost:8000/api/v1/health` → API health check
- `http://localhost:8000/docs` → Swagger API documentation

---

### Option 2: Local File (No Server Required)

Open the HTML file directly in your browser:

**Path:**
```
C:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\artifacts\ARTIFACT_INDEX.html
```

**Quick launch:**
```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\artifacts"
.\OPEN_ARTIFACT_VIEWER.bat
```

Or double-click: `agent-orchestrator\artifacts\OPEN_ARTIFACT_VIEWER.bat`

**Limitations:**
- File protocol (`file:///`) may have browser restrictions
- Some features may require server (CORS, file loading)
- No API integration

---

### Option 3: Python HTTP Server (Simple)

Use Python's built-in HTTP server:

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\artifacts"
python -m http.server 9000
```

Then open: `http://localhost:9000/ARTIFACT_INDEX.html`

**Pros:**
- Simple, no configuration
- Works with all browser features

**Cons:**
- No API integration
- Port 9000 (not standard)
- No CORS handling

---

## Recommended Setup: FastAPI Backend

### Why FastAPI hosting is best:

1. **Integrated with API** - Access artifacts and API from same origin
2. **CORS configured** - No cross-origin issues
3. **Standard port** - Uses port 8000 (already configured)
4. **API access** - Can query artifact data via API endpoints
5. **Production ready** - Can scale with uvicorn workers

### Configuration added:

**File:** `agent-orchestrator/app/main.py`

**Changes:**
- Added `StaticFiles` import
- Mounted `/artifacts` directory
- Added root route (`/`) redirecting to viewer
- Added `/viewer` route serving viewer directly

**Static file access:**
- All files in `artifacts/` directory accessible via `/artifacts/` URL path
- Example: `/artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json`

---

## Quick Start

### 1. Start the FastAPI server:

```powershell
cd "c:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open browser:

Navigate to: `http://localhost:8000/`

### 3. Verify:

- ✅ Artifact viewer loads
- ✅ 104 artifacts displayed
- ✅ Search works
- ✅ Tabs work
- ✅ Action buttons work

---

## Production Deployment

For production, use multiple workers:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or with Gunicorn:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Port Configuration

From `infrastructure/ports.registry.json`:

- **Backend API:** Port 8000 (internal)
- **Artifact viewer:** Served via backend at `http://localhost:8000/`
- **Static files:** Mounted at `/artifacts/` path

No additional port needed - viewer uses existing backend port.

---

**Recommended:** Use FastAPI hosting for best integration and features.
