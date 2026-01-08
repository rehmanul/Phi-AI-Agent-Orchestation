# Content Interaction & Multi-Agent Workflow Integration Plan

**Date:** 2026-01-07  
**Goal:** Enable users to interact with generated artifacts and integrate review console with FastAPI backend  
**Status:** PLANNING

---

## Executive Summary

The artifact review console currently shows 0 artifacts and "Server: Checking..." because it's not connected to the FastAPI backend. This plan outlines the multi-step approach to:

1. **Connect artifact viewer to FastAPI backend** - Load artifacts from API instead of static JSON
2. **Add review/approval endpoints** - Enable approval/rejection via web UI
3. **Implement LLM handoff preparation** - Generate "One-Look Brief" for approved artifacts
4. **Create interactive artifact viewer** - Allow inline editing and commenting
5. **Build multi-agent orchestration UI** - Visualize and control agent workflows

---

## Phase 1: Backend API Integration (CRITICAL - Blocks Everything)

### 1.1 Fix API Endpoint Mismatches

**Problem:** The HTML viewer calls endpoints that don't match FastAPI routes:
- HTML calls: `/api/health`, `/api/reviews`, `/api/brief`
- FastAPI has: `/api/v1/health`, `/api/v1/workflows/{id}/review-queue`, etc.

**Solution:** Create adapter endpoints or update HTML to use correct paths.

**Implementation:**
```python
# app/main.py - Add convenience endpoints
@app.get("/api/health")  # Alias for /api/v1/health
@app.get("/api/reviews")  # Aggregate all review queues
@app.post("/api/brief")  # Generate One-Look Brief
```

**Files to Modify:**
- `app/main.py` - Add convenience endpoints
- `artifacts/ARTIFACT_INDEX.html` - Update API_BASE configuration

---

### 1.2 Create Artifact Index API Endpoint

**Problem:** Viewer loads static JSON file instead of live API data.

**Solution:** Create `/api/v1/artifacts/index` endpoint that:
- Scans artifacts directory dynamically
- Returns categorized artifact list
- Includes review status from queues
- Provides artifact metadata

**Implementation:**
```python
# app/routes.py
@router.get("/artifacts/index")
async def get_artifact_index(
    storage: WorkflowStorage = Depends(get_storage)
) -> Dict[str, Any]:
    """
    Get comprehensive artifact index with review status.
    Returns same structure as ARTIFACT_INDEX.json but with live data.
    """
    # Scan artifacts directory
    # Load review queues
    # Merge review status into artifacts
    # Return categorized index
```

**Files to Create/Modify:**
- `app/routes.py` - Add `/artifacts/index` endpoint
- `artifacts/ARTIFACT_INDEX.html` - Fetch from API instead of embedded JSON

---

### 1.3 Add Server Status Check

**Problem:** "Server: Checking..." never resolves.

**Solution:** Implement proper health check endpoint and status indicator.

**Implementation:**
```javascript
// Check server health on page load
async function checkServerStatus() {
    try {
        const response = await fetch('/api/v1/health');
        const data = await response.json();
        if (data.status === 'healthy') {
            document.getElementById('server-status').textContent = '• Server: Online';
            document.getElementById('server-status').style.color = 'green';
            return true;
        }
    } catch (e) {
        document.getElementById('server-status').textContent = '• Server: Offline';
        document.getElementById('server-status').style.color = 'red';
        return false;
    }
}
```

**Files to Modify:**
- `artifacts/ARTIFACT_INDEX.html` - Add server status check function

---

## Phase 2: Review & Approval Integration

### 2.1 Connect Review Queues to API

**Problem:** Review console shows 0 artifacts because it's not loading from review queues.

**Solution:** Create endpoints to fetch review queues and integrate with artifact viewer.

**Implementation:**
```python
# app/routes.py
@router.get("/review-queues/summary")
async def get_review_queues_summary(
    storage: WorkflowStorage = Depends(get_storage)
) -> Dict[str, Any]:
    """
    Get summary of all review queues:
    - HR_PRE: Pending count, approved count
    - HR_LANG: Pending count, approved count
    - HR_MSG: Pending count, approved count
    - HR_RELEASE: Pending count, approved count
    """
```

**Files to Create/Modify:**
- `app/routes.py` - Add review queue summary endpoint
- `artifacts/ARTIFACT_INDEX.html` - Load review status from API

---

### 2.2 Add Inline Approval/Rejection

**Problem:** Users must use CLI scripts to approve artifacts.

**Solution:** Add approve/reject buttons directly in artifact viewer.

**Implementation:**
```python
# app/routes.py
@router.post("/artifacts/{artifact_path}/review")
async def review_artifact(
    artifact_path: str,
    decision: str,  # "approve" or "reject"
    rationale: Optional[str] = None,
    review_gate: ReviewGateID
):
    """Approve or reject artifact via web UI."""
    # Update artifact status
    # Update review queue
    # Log to audit
    # Return success
```

**Files to Create/Modify:**
- `app/routes.py` - Add artifact review endpoint
- `artifacts/ARTIFACT_INDEX.html` - Add approve/reject buttons
- `app/review_sync.py` - Ensure file sync works

---

## Phase 3: LLM Handoff Preparation

### 3.1 One-Look Brief Generator

**Problem:** User wants to prepare artifacts for LLM interaction but no automated brief exists.

**Solution:** Implement "One-Look Brief" generator that:
- Aggregates approved artifacts
- Answers: What, Why, Who, How, What Exactly is Being Sent
- Formats for LLM consumption
- Exports to markdown/JSON

**Implementation:**
```python
# app/routes.py
@router.post("/api/v1/artifacts/generate-brief")
async def generate_one_look_brief(
    artifact_paths: List[str],
    format: str = "markdown"  # "markdown" or "json"
) -> Dict[str, Any]:
    """
    Generate comprehensive briefing document for LLM handoff.
    
    Structure:
    - Executive Summary (What)
    - Rationale & Context (Why)
    - Stakeholders & Recipients (Who)
    - Delivery Method & Timeline (How)
    - Exact Content Being Sent (What Exactly)
    """
```

**Files to Create:**
- `app/brief_generator.py` - Brief generation logic
- `app/routes.py` - Add brief generation endpoint
- `artifacts/ARTIFACT_INDEX.html` - Add "Generate Brief" button

---

### 3.2 LLM-Ready Export Format

**Problem:** Artifacts need to be formatted for LLM consumption.

**Solution:** Create standardized export format with:
- Structured JSON schema
- Metadata preservation
- Human-readable markdown
- Token count estimation

**Implementation:**
```python
# app/llm_export.py
class LLMExporter:
    def export_artifacts(
        self,
        artifacts: List[str],
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export artifacts in LLM-ready format.
        - Flatten nested structures
        - Add context headers
        - Preserve metadata
        - Estimate token count
        """
```

**Files to Create:**
- `app/llm_export.py` - LLM export utilities
- `app/routes.py` - Add export endpoint

---

## Phase 4: Interactive Content Editing

### 4.1 Inline Artifact Viewer

**Problem:** Users can't view/edit artifact content in the console.

**Solution:** Add expandable artifact viewer with:
- JSON editor with syntax highlighting
- Diff view (before/after approval)
- Comment/annotation system
- Save changes back to artifact

**Implementation:**
```javascript
// artifacts/ARTIFACT_INDEX.html
function openArtifactEditor(artifactPath) {
    // Fetch artifact content
    // Display in Monaco editor (VS Code editor in browser)
    // Allow editing
    // Save back to API
}
```

**Files to Create/Modify:**
- `artifacts/ARTIFACT_INDEX.html` - Add artifact editor modal
- `app/routes.py` - Add artifact update endpoint
- Use Monaco Editor or CodeMirror for JSON editing

---

### 4.2 Comment & Annotation System

**Problem:** No way to add notes to artifacts during review.

**Solution:** Add comment system that:
- Allows inline comments on artifacts
- Associates comments with review decisions
- Persists comments in artifact metadata
- Shows comment history

**Implementation:**
```python
# app/models.py
class ArtifactComment(BaseModel):
    artifact_path: str
    comment: str
    author: str
    timestamp: datetime
    review_decision: Optional[str]  # "approve", "reject", "request_changes"
```

**Files to Create/Modify:**
- `app/models.py` - Add comment model
- `app/routes.py` - Add comment endpoints
- `artifacts/ARTIFACT_INDEX.html` - Add comment UI

---

## Phase 5: Multi-Agent Workflow Visualization

### 5.1 Agent Status Dashboard

**Problem:** No visibility into agent execution and workflow progress.

**Solution:** Create real-time agent dashboard showing:
- Active agents (RUNNING status)
- Agent outputs (artifact generation)
- Blocked agents (WAITING_REVIEW)
- Agent dependencies and data flow

**Implementation:**
```python
# app/routes.py
@router.get("/api/v1/agents/status")
async def get_agent_status() -> Dict[str, Any]:
    """
    Get real-time agent status:
    - Active agents
    - Recent outputs
    - Dependencies
    - Blocking conditions
    """
```

**Files to Create:**
- `app/agent_dashboard.py` - Agent status aggregation
- `artifacts/AGENT_DASHBOARD.html` - New dashboard page
- WebSocket connection for real-time updates (optional)

---

### 5.2 Workflow Orchestration UI

**Problem:** Cannot trigger agent workflows from UI.

**Solution:** Build orchestration interface allowing:
- Manual agent spawning
- Workflow state advancement
- Agent execution triggering
- Dependency visualization

**Implementation:**
```python
# app/routes.py - Use existing endpoints
# GET /api/v1/workflows/{id}/agents - List agents
# POST /api/v1/workflows/{id}/agents/spawn - Spawn agent
# POST /api/v1/workflows/{id}/agents/execute - Execute agent
```

**Files to Create:**
- `artifacts/ORCHESTRATION_UI.html` - Orchestration interface
- `artifacts/ARTIFACT_INDEX.html` - Link to orchestration UI

---

## Implementation Priority

### 🔴 CRITICAL (Must Have for Basic Functionality)
1. ✅ **Phase 1.1** - Fix API endpoint mismatches (30 min)
2. ✅ **Phase 1.2** - Create artifact index API endpoint (1 hour)
3. ✅ **Phase 1.3** - Add server status check (15 min)

### 🟡 HIGH (Enables Core Interaction)
4. **Phase 2.1** - Connect review queues to API (1 hour)
5. **Phase 2.2** - Add inline approval/rejection (2 hours)

### 🟢 MEDIUM (Enhances User Experience)
6. **Phase 3.1** - One-Look Brief Generator (2 hours)
7. **Phase 4.1** - Inline artifact viewer (3 hours)

### 🔵 LOW (Nice to Have)
8. **Phase 3.2** - LLM export format (1 hour)
9. **Phase 4.2** - Comment system (2 hours)
10. **Phase 5.1** - Agent dashboard (2 hours)
11. **Phase 5.2** - Orchestration UI (3 hours)

---

## Technical Architecture

### API Layer
```
FastAPI Backend (port 8000)
├── /api/v1/health (health check)
├── /api/v1/artifacts/index (artifact catalog)
├── /api/v1/review-queues/summary (review status)
├── /api/v1/artifacts/{path}/review (approve/reject)
├── /api/v1/artifacts/generate-brief (LLM brief)
└── /api/v1/agents/status (agent dashboard)
```

### Frontend Layer
```
Artifact Viewer (HTTP served from /artifacts/)
├── ARTIFACT_INDEX.html (main viewer)
├── AGENT_DASHBOARD.html (agent status)
└── ORCHESTRATION_UI.html (workflow control)
```

### Data Flow
```
1. User opens viewer → Fetches /api/v1/artifacts/index
2. Viewer displays artifacts → Shows review status
3. User clicks approve → POST /api/v1/artifacts/{path}/review
4. Backend updates artifact → Syncs to review queue files
5. User generates brief → POST /api/v1/artifacts/generate-brief
6. Brief returned → Displayed in modal/downloaded
```

---

## Next Steps (Immediate)

1. **Fix API endpoints** (Phase 1.1) - Update HTML to use `/api/v1/health`
2. **Create artifact index endpoint** (Phase 1.2) - Dynamic artifact loading
3. **Add server status check** (Phase 1.3) - Real-time status indicator
4. **Test end-to-end** - Verify viewer loads artifacts from API

**Estimated Time:** 2-3 hours for critical fixes

---

## Success Criteria

✅ **Phase 1 Complete:**
- Viewer loads artifacts from API (not static JSON)
- Server status shows "Online" when backend is running
- Artifact counts display correctly (104 total)

✅ **Phase 2 Complete:**
- Review queues display in viewer
- Users can approve/reject artifacts via UI
- Approval status updates immediately

✅ **Phase 3 Complete:**
- One-Look Brief generates successfully
- Brief answers all 5 questions (What/Why/Who/How/What Exactly)
- Brief can be exported/downloaded

✅ **Phase 4 Complete:**
- Users can view artifact content inline
- Users can add comments to artifacts
- Changes persist to artifact files

✅ **Phase 5 Complete:**
- Agent dashboard shows real-time status
- Users can spawn/trigger agents from UI
- Workflow dependencies visualized

---

**Ready to proceed with Phase 1 (Critical API Integration)?**
