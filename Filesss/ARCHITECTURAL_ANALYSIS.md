# Risk Management Workflow System - Architectural Analysis

## PHASE 1 — CODEBASE INTERROGATION

### Repository Structure

**Entry Points:**
- `api/main.py` - FastAPI application (port 8002)
- `START_SYSTEM.bat` - Windows launcher script
- No CLI entry point observed
- No background worker/daemon process observed

**Orchestration Logic:**
- `agents/orchestrator/workflow_engine.py` - `WorkflowEngine` class
  - Single state file: `workflow_state.json` (root directory)
  - Methods: `start_workflow()`, `update_phase()`
  - State structure: `{workflow_id, document_id, file_path, current_phase, status, phases: {}}`

**Agent Abstractions:**
- **Orchestrator Pattern**: Each phase has an orchestrator class
  - `IntakeOrchestrator` - Phase 1
  - `RiskScanOrchestrator` - Phase 2
  - `RuinGateOrchestrator` - Phase 5
  - Individual agents (no orchestrator observed for phases 3, 4, 6, 7)

**Persistence Mechanisms:**
- **File-based JSON storage** (no database)
- State locations:
  - `workflow_state.json` - Single workflow state (root)
  - `data/processed/intake/intake_{document_id}.json` - Phase 1 results
  - `data/processed/risk_scan/risk_scan_{document_id}.json` - Phase 2 results
  - `data/processed/ruin_gates/ruin_gates_{timestamp}.json` - Phase 5 results
  - `data/memory/historical/{record_id}.json` - Historical data
  - `data/memory/near_misses/{miss_id}.json` - Near misses
  - `data/memory/assumptions/{log_id}.json` - Assumption logs
  - `data/logs/decisions/{log_id}.json` - Decision logs
  - `data/execution/{exec_id}.json` - Execution tracking
  - `data/learning/{update_id}.json` - Model updates

**Existing APIs/Ports:**
- FastAPI server on port 8002
- Endpoints observed:
  - `GET /` - Root
  - `GET /health` - Health check
  - `POST /api/intake/upload` - File upload
  - `POST /api/intake/process` - Trigger processing
  - `GET /api/intake/status/{document_id}` - Get intake results
  - `GET /api/intake/list` - List processed documents
  - `POST /api/workflow/start` - Start workflow
  - `GET /api/workflow/status/{workflow_id}` - Get workflow state

### Mental Model

**How Tasks Are Created:**
1. User uploads file via `POST /api/intake/upload`
2. File saved to `data/raw/{filename}`
3. User calls `POST /api/intake/process` with filename
4. `IntakeOrchestrator.process_document()` executes synchronously
5. Results saved to `data/processed/intake/intake_{document_id}.json`

**How Tasks Move Through System:**
- **No automatic progression observed**
- Each phase must be invoked explicitly via API
- `WorkflowEngine.update_phase()` updates state but doesn't trigger next phase
- Phases are **decoupled** - no automatic chaining

**How Agents Execute Work:**
- **Synchronous execution** (no async/await in orchestrators)
- Each orchestrator:
  1. Takes input data (previous phase results)
  2. Calls sub-agents sequentially
  3. Combines results
  4. Saves to JSON file
  5. Returns result dict

**How Outputs Are Routed:**
- **File-based routing** - outputs saved to phase-specific directories
- **No message queue or event system**
- Frontend must poll for results
- Each phase writes its own output file

**Where State Lives:**
- **Workflow-level state**: `workflow_state.json` (single file, overwrites)
- **Phase-level state**: Individual JSON files per phase result
- **No in-memory state** (stateless API handlers)
- **No shared state** between requests

**Where Failures Are Handled:**
- Try/except blocks in API routes return HTTPException
- No retry logic observed
- No failure state persistence
- Errors logged to console only

### Explicit Answers

**Primary Execution Model:**
- **Request-response HTTP API** (FastAPI)
- **Synchronous processing** - API calls block until completion
- **No background jobs** - all work happens in request handler
- **No task queue** - no Celery, RQ, or similar

**Objects Representing "State of Truth":**
1. **`workflow_state.json`** - Current workflow phase and status
2. **Phase result JSON files** - Authoritative phase outputs
   - `intake_{document_id}.json`
   - `risk_scan_{document_id}.json`
   - `ruin_gates_{timestamp}.json`
3. **Raw files in `data/raw/`** - Source documents (immutable)

**Data Persisted vs Ephemeral:**
- **Persisted:**
  - All phase results (JSON files)
  - Workflow state
  - Historical data, near misses, assumptions
  - Decision logs
  - Execution tracking
- **Ephemeral:**
  - LLM API responses (not cached)
  - In-memory orchestrator instances (recreated per request)
  - No session state

**Safe to Expose to Frontend:**
- ✅ All phase result JSON files (read-only)
- ✅ Workflow state (read-only)
- ✅ Historical data queries
- ✅ Decision logs (read-only)
- ⚠️ File upload (requires validation)
- ❌ Direct orchestrator instantiation (must go through API)
- ❌ Direct file system access (must go through API)

---

## PHASE 2 — FRONTEND REQUIREMENTS DISCOVERY

### What Frontend Can Observe Safely

**Read-Only Views:**
1. **Workflow State**
   - Current phase
   - Status (in_progress, complete, stopped)
   - Phase results (if complete)
   - Timestamps

2. **Phase Results**
   - Intake: assumptions, failure-first analysis
   - Risk Scan: tail risks, incentives, regulatory
   - Modeling: bounds, scenarios, stress tests
   - Ruin Gates: gate evaluations, STOP/PROCEED status
   - Judgment: confidence, decisions
   - Execution: tracking data, monitoring

3. **Historical Data**
   - Past workflows
   - Near misses
   - Assumption logs
   - Decision history

### What Frontend Cannot Control Directly

**Blocked Actions:**
1. **Phase Progression** - No API endpoint to advance phases
2. **Orchestrator Configuration** - LLM provider/model hardcoded
3. **File System Structure** - Directories managed by orchestrators
4. **State File Location** - Fixed to `workflow_state.json`

**Requires Backend Changes:**
- Phase progression API
- Workflow pause/resume
- Phase retry/rerun
- Configuration updates

### Operations Requiring Async Handling

**Long-Running Operations:**
1. **Document Processing** (`POST /api/intake/process`)
   - Document parsing
   - LLM calls (hidden assumptions, failure-first)
   - **Blocks until complete** (no async/background job)

2. **Risk Scanning** (not yet exposed via API)
   - Three LLM agents run sequentially
   - Each can take 10-30 seconds

3. **Modeling** (not yet exposed via API)
   - Scenario tree building (LLM)
   - Stress testing

**Frontend Must:**
- Show loading states during processing
- Poll for completion (no WebSocket)
- Handle timeouts gracefully
- Allow user to navigate away and return

### Operations Requiring Gating/Approval

**Human Approval Points:**
1. **Phase 6: Human Judgment**
   - `DecisionLogger.log_decision()` exists
   - No API endpoint observed for approval/rejection
   - No workflow pause at this phase

2. **Phase 5: Ruin Gates**
   - `should_stop` flag in results
   - No automatic workflow halt
   - Frontend must enforce STOP condition

**Missing Gates:**
- No API to pause workflow at judgment phase
- No API to submit approval/rejection
- No API to override ruin gates (with audit)

---

## PHASE 3 — API & BOUNDARY DESIGN

### Missing Backend Interfaces

**Required API Endpoints (Not Currently Exposed):**

1. **Phase Execution Endpoints**
   - `POST /api/workflow/{workflow_id}/phase/{phase_name}/execute`
   - `GET /api/workflow/{workflow_id}/phase/{phase_name}/status`
   - `POST /api/workflow/{workflow_id}/phase/{phase_name}/retry`

2. **Risk Scan Endpoints**
   - `POST /api/risk_scan/{document_id}/scan`
   - `GET /api/risk_scan/{document_id}/status`

3. **Modeling Endpoints**
   - `POST /api/modeling/{workflow_id}/calculate`
   - `GET /api/modeling/{workflow_id}/results`

4. **Ruin Gates Endpoints**
   - `POST /api/ruin_gates/{workflow_id}/evaluate`
   - `GET /api/ruin_gates/{workflow_id}/status`

5. **Judgment Endpoints**
   - `POST /api/judgment/{workflow_id}/review`
   - `POST /api/judgment/{workflow_id}/approve`
   - `POST /api/judgment/{workflow_id}/reject`

6. **Workflow Control**
   - `POST /api/workflow/{workflow_id}/pause`
   - `POST /api/workflow/{workflow_id}/resume`
   - `POST /api/workflow/{workflow_id}/advance`

7. **List/Query Endpoints**
   - `GET /api/workflow/` - List all workflows
   - `GET /api/workflow/{workflow_id}/phases` - Get all phase results

### API Design Decision

**REST vs Embedded Next.js API Routes:**
- **Recommendation: REST (FastAPI)**
  - Backend already FastAPI
  - Business logic in Python agents
  - No need to duplicate in TypeScript
  - Clear separation of concerns

**WebSocket vs Polling:**
- **Recommendation: Polling First**
  - No WebSocket infrastructure exists
  - Synchronous processing (no background jobs)
  - Simple to implement
  - Can add WebSocket later if needed

**File Streaming vs Structured JSON:**
- **Current: Structured JSON** (all results in JSON)
- **Recommendation: Keep JSON**
  - Phase results are structured data
  - No need for streaming
  - File downloads can be separate endpoint if needed

### Endpoint Contracts (Proposed)

```
# Workflow Management
GET    /api/workflow/                    # List all workflows
POST   /api/workflow/start               # Start new workflow
GET    /api/workflow/{workflow_id}       # Get workflow state
POST   /api/workflow/{workflow_id}/advance  # Advance to next phase
POST   /api/workflow/{workflow_id}/pause   # Pause workflow
POST   /api/workflow/{workflow_id}/resume  # Resume workflow

# Phase Execution
POST   /api/workflow/{workflow_id}/phase/intake/execute
POST   /api/workflow/{workflow_id}/phase/risk_scan/execute
POST   /api/workflow/{workflow_id}/phase/modeling/execute
POST   /api/workflow/{workflow_id}/phase/ruin_gates/execute
GET    /api/workflow/{workflow_id}/phase/{phase_name}/status

# Phase Results (Read-Only)
GET    /api/workflow/{workflow_id}/phases/intake
GET    /api/workflow/{workflow_id}/phases/risk_scan
GET    /api/workflow/{workflow_id}/phases/modeling
GET    /api/workflow/{workflow_id}/phases/ruin_gates
GET    /api/workflow/{workflow_id}/phases/judgment
GET    /api/workflow/{workflow_id}/phases/execution

# Human Actions
POST   /api/workflow/{workflow_id}/judgment/review    # Submit review
POST   /api/workflow/{workflow_id}/judgment/approve   # Approve workflow
POST   /api/workflow/{workflow_id}/judgment/reject    # Reject workflow

# Historical Data
GET    /api/memory/historical?filters={}  # Query historical data
GET    /api/memory/near_misses?criteria={}  # Query near misses
GET    /api/memory/assumptions?document_id={}  # Get assumption logs
```

---

## PHASE 4 — FRONTEND SCAFFOLD PLAN

### Core Pages

1. **Dashboard** (`/`)
   - Workflow list
   - System status
   - Quick actions

2. **Workflow Detail** (`/workflow/[id]`)
   - Phase navigation
   - Current phase display
   - Phase status indicators

3. **Phase Pages** (`/workflow/[id]/[phase]`)
   - Phase 1: Intake - File upload, assumptions
   - Phase 2: Risk Scan - Three-column risk display
   - Phase 3: Modeling - Bounds, scenarios, visualizations
   - Phase 4: Memory - Historical context
   - Phase 5: Ruin Gates - **Critical STOP/PROCEED display**
   - Phase 6: Judgment - Review interface, approval
   - Phase 7: Execution - Tracking, monitoring

### Core Components

1. **PhaseNavigation** - 7-phase sidebar (exists)
2. **StatusBanner** - System health (exists)
3. **WorkflowStatusCard** - Current phase, status
4. **PhaseResultViewer** - Display phase results
5. **RuinGateDisplay** - Large STOP/PROCEED indicator
6. **ApprovalWorkflow** - Review checklist, approve/reject
7. **DocumentUpload** - File upload with progress
8. **LoadingState** - Processing indicators

### Shared Types

```typescript
// Mirror backend schemas
interface WorkflowState {
  workflow_id: string;
  document_id: string;
  current_phase: Phase;
  status: 'in_progress' | 'complete' | 'stopped' | 'paused';
  phases: Record<Phase, PhaseResult>;
  created_at: string;
  updated_at?: string;
}

type Phase = 
  | 'intake' 
  | 'risk_scan' 
  | 'modeling' 
  | 'memory' 
  | 'ruin_gates' 
  | 'judgment' 
  | 'execution';

interface PhaseResult {
  phase: Phase;
  status: 'complete' | 'in_progress' | 'error';
  data?: any; // Phase-specific
  completed_at?: string;
}
```

### State Management Approach

**Recommendation: React Query (TanStack Query)**
- Already installed
- Handles API state
- Caching and refetching
- Polling support

**Local State:**
- Form inputs (React Hook Form)
- UI state (open/closed modals)
- File upload progress

**No Global State Needed:**
- Workflow state fetched per route
- No shared state between pages
- Stateless API

---

## PHASE 5 — EXECUTION CHECK

### What Will Be Built First

**Priority 1: Core Workflow Navigation**
- Workflow list page
- Workflow detail page with phase navigation
- Phase result viewing (read-only)

**Priority 2: Phase 1 (Intake) - Complete**
- File upload (exists)
- Processing status (exists)
- Results display (exists)

**Priority 3: Phase 5 (Ruin Gates) - Critical**
- Gate evaluation display
- STOP/PROCEED indicator
- Block progression if STOP

**Priority 4: Phase 6 (Judgment) - Human-in-Loop**
- Review interface
- Approval/rejection controls
- Decision logging

### What Will Be Deferred

- Phase 2-4, 7 full implementations (read-only views first)
- Advanced visualizations (charts, trees)
- Real-time updates (WebSocket)
- Historical data query interface
- Model parameter adjustments

### Assumptions Made

1. **Backend will expose missing endpoints** (phases 2-7 execution)
2. **Synchronous processing is acceptable** (user waits for completion)
3. **File-based state is sufficient** (no database migration needed)
4. **Single workflow at a time** (workflow_state.json overwrites)
5. **No authentication required** (development phase)

### What Would Break If Assumptions Wrong

**If backend doesn't expose phase endpoints:**
- Frontend cannot trigger phases 2-7
- Must manually call orchestrators (not acceptable)
- **Mitigation**: Build API endpoints first

**If processing becomes async/background:**
- Polling mechanism needed
- Status endpoints required
- **Mitigation**: Add polling to React Query

**If multiple workflows needed:**
- `workflow_state.json` single-file limitation
- Need workflow ID-based state files
- **Mitigation**: Modify `WorkflowEngine` to use `workflow_{id}.json`

**If authentication required:**
- No auth in current API
- Must add auth middleware
- **Mitigation**: Add JWT/auth later

---

## OBSERVED vs PROPOSED

### OBSERVED (From Code)

- FastAPI server on port 8002
- File-based JSON persistence
- Synchronous phase execution
- Single workflow state file
- Phase orchestrators exist but not all exposed via API
- Intake phase fully functional via API
- Workflow engine exists but minimal
- No automatic phase progression
- No background job system
- No WebSocket/real-time infrastructure

### PROPOSED (Not Yet Implemented)

- Phase execution endpoints (2-7)
- Workflow control endpoints (pause/resume/advance)
- Workflow listing endpoint
- Judgment approval/rejection endpoints
- Polling-based status updates
- Multiple workflow support (ID-based state files)
- Error state persistence
- Retry mechanisms

---

## Frontend Capability Matrix

| Capability | Backing Backend Object/Method | Risk Level | Required Backend Change |
|------------|------------------------------|------------|------------------------|
| List workflows | `GET /api/workflow/` | **HIGH** | Create endpoint to scan workflow state files |
| View workflow state | `GET /api/workflow/status/{id}` | Low | None (exists) |
| Start workflow | `POST /api/workflow/start` | Low | None (exists) |
| Upload document | `POST /api/intake/upload` | Low | None (exists) |
| Process intake | `POST /api/intake/process` | Low | None (exists) |
| View intake results | `GET /api/intake/status/{id}` | Low | None (exists) |
| Execute risk scan | `RiskScanOrchestrator.scan_risks()` | **HIGH** | Create API endpoint |
| View risk scan results | Read JSON file | Medium | Create API endpoint for consistency |
| Execute modeling | `BoundsCalculator`, etc. | **HIGH** | Create API endpoint + orchestrator |
| View modeling results | Read JSON file | Medium | Create API endpoint |
| Evaluate ruin gates | `RuinGateOrchestrator.evaluate_gates()` | **HIGH** | Create API endpoint |
| View ruin gates | Read JSON file | Medium | Create API endpoint |
| Submit judgment | `DecisionLogger.log_decision()` | **HIGH** | Create API endpoint + workflow pause |
| Approve/reject workflow | None | **HIGH** | Create API endpoint + state update |
| Advance workflow phase | `WorkflowEngine.update_phase()` | Medium | Create API endpoint |
| Pause/resume workflow | None | **HIGH** | Add pause/resume state + API |
| View execution tracking | Read JSON file | Medium | Create API endpoint |
| Query historical data | `HistoricalDataManager.query()` | Medium | Create API endpoint |
| View decision logs | Read JSON file | Medium | Create API endpoint |

---

## Critical Gaps Identified

1. **No Phase Execution API** - Phases 2-7 cannot be triggered from frontend
2. **No Workflow Progression Logic** - Manual phase advancement required
3. **Single Workflow Limitation** - `workflow_state.json` overwrites
4. **No Human Approval Gate** - Judgment phase doesn't pause workflow
5. **No Error Recovery** - Failed phases have no retry mechanism
6. **No Status Polling** - Long-running operations have no status endpoint

---

**End of Analysis**
