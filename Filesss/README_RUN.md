# Agent Orchestrator API - Usage Guide

## Overview

The Agent Orchestrator API is a FastAPI service that manages legislative workflow states, artifacts, and review gates according to strict invariants defined in `AUTHORITATIVE_INVARIANTS.md`.

## Master System Architecture Diagram

**Authoritative Source:** `.userInput/agent orchestrator 1.6.mmd`

The complete system architecture is defined in the master diagram (939 lines), which serves as the authoritative source for all system design decisions. This diagram shows:

- **Legislative Process Spine:** PRE_EVT → INTRO_EVT → COMM_EVT → FLOOR_EVT → FINAL_EVT → IMPL_EVT
- **AI Service Execution Layer:** Multi-source ingestion, contextual retrieval, feature extraction, draft & strategy generation, impact & risk scoring
- **Human Review Gates:** HR_PRE, HR_LANG, HR_MSG, HR_RELEASE
- **Memory & Learning Systems:** Evidence store, tactic performance history, narrative effectiveness log, legislative outcomes, causal attribution engine
- **Execution Loop:** Strategy decomposition, tactical planning, tactic execution engine, live monitoring, tactical retuning
- **Agent Orchestration Model:** Orchestrator logic, agent types (Intelligence, Drafting, Execution, Learning), agent lifecycle, hard safety constraints

All system components, state machines, and agent behaviors must align with the master diagram.

**Reference Documentation:**
- **Master Diagram Reference:** [`MASTER_DIAGRAM_REFERENCE.md`](MASTER_DIAGRAM_REFERENCE.md) - Complete master diagram documentation
- **Component Mapping:** [`COMPONENT_MAPPING.md`](COMPONENT_MAPPING.md) - Code-to-diagram element mappings
- **Diagram Index:** [`diagrams/DIAGRAM_INDEX.md`](diagrams/DIAGRAM_INDEX.md) - Catalog of all derived diagrams

**Validation:**
Run alignment checks to ensure code matches master diagram:
```bash
python scripts/check_master_alignment.py
```

## Installation

```bash
cd agent-orchestrator
pip install -r requirements.txt
```

## Running the Service

### Development Mode

```bash
cd agent-orchestrator/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the service is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```http
GET /api/v1/health
```

Returns service health status, active workflows, and workflows in error state.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-20T12:00:00Z",
  "active_workflows": 5,
  "workflows_in_error": 0
}
```

---

### Create Workflow

```http
POST /api/v1/workflows
Content-Type: application/json

{
  "initial_state": "PRE_EVT",
  "metadata": {
    "description": "Example workflow"
  }
}
```

Creates a new workflow starting in the specified legislative state (default: `PRE_EVT`).

**Response:**
```json
{
  "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
  "legislative_state": "PRE_EVT",
  "orchestrator_state": "ORCH_IDLE",
  "created_at": "2026-01-20T12:00:00Z"
}
```

---

### Get Workflow Status

```http
GET /api/v1/workflows/{workflow_id}/status
```

Returns comprehensive workflow status including:
- Current legislative and orchestrator states
- Pending review gates
- Required artifacts status
- Artifacts summary (exists, missing, approved, pending)
- Blocking issues preventing state advancement
- Last error diagnostic

**Response:**
```json
{
  "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
  "legislative_state": "PRE_EVT",
  "orchestrator_state": "ORCH_ACTIVE",
  "pending_gates": ["HR_PRE"],
  "required_artifacts_status": {
    "Concept Memo": {
      "artifact_name": "Concept Memo",
      "required": true,
      "exists": true,
      "artifact_id": "artifact-123",
      "created_at": "2026-01-20T12:00:00Z",
      "requires_review": true,
      "review_gate": "HR_PRE",
      "review_status": "PENDING",
      "approved_at": null,
      "approved_by": null
    },
    "Stakeholder Landscape Map": {
      "artifact_name": "Stakeholder Landscape Map",
      "required": true,
      "exists": false,
      "artifact_id": null,
      "created_at": null,
      "requires_review": false,
      "review_gate": null,
      "review_status": null,
      "approved_at": null,
      "approved_by": null
    }
  },
  "artifacts_summary": {
    "exists": 1,
    "missing": 1,
    "approved": 0,
    "pending": 1
  },
  "last_error": null,
  "can_advance": false,
  "blocking_issues": [
    "Missing required artifact: Stakeholder Landscape Map",
    "Artifact 'Concept Memo' not approved via HR_PRE"
  ]
}
```

---

### Advance State

```http
POST /api/v1/workflows/{workflow_id}/advance
Content-Type: application/json

{
  "target_state": "INTRO_EVT",
  "external_confirmation": {
    "event_type": "bill_vehicle_identified",
    "confirmed_by": "human:john.doe",
    "source_reference": "congress.gov/bill/123",
    "metadata": {
      "bill_number": "HR-1234",
      "congress": 119
    }
  },
  "metadata": {}
}
```

Advances workflow to the next legislative state. **Strictly validates**:
- Sequential progression (no skipping)
- Required artifacts exist and are approved
- Required review gates are approved
- External confirmation matches required event type
- Orchestrator state allows advancement

**Response (Success):**
```json
{
  "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
  "previous_state": "PRE_EVT",
  "new_state": "INTRO_EVT",
  "advanced_at": "2026-01-20T12:00:00Z",
  "diagnostics": []
}
```

**Response (Validation Failure - 400):**
```json
{
  "detail": {
    "error_code": "TRANSITION_VALIDATION_FAILED",
    "message": "State transition validation failed",
    "blocking_issues": [
      "Missing required artifact: Concept Memo",
      "Review gate HR_PRE not approved"
    ],
    "correlation_id": "456e7890-e89b-12d3-a456-426614174001",
    "diagnostic_ids": ["diag-123", "diag-124"]
  }
}
```

---

### Submit Artifact

```http
POST /api/v1/workflows/{workflow_id}/artifacts
Content-Type: application/json

{
  "artifact_name": "Concept Memo",
  "artifact_data": {
    "title": "Policy Concept",
    "summary": "This memo outlines...",
    "content": "..."
  },
  "requires_review": true,
  "review_gate": "HR_PRE"
}
```

Submits an artifact to the workflow. Validates:
- Artifact dependencies (if any) exist and are approved
- Artifact is expected for current state

**Response:**
```json
{
  "artifact_name": "Concept Memo",
  "artifact_id": "artifact-123",
  "status": {
    "artifact_name": "Concept Memo",
    "required": true,
    "exists": true,
    "artifact_id": "artifact-123",
    "created_at": "2026-01-20T12:00:00Z",
    "requires_review": true,
    "review_gate": "HR_PRE",
    "review_status": "PENDING",
    "approved_at": null,
    "approved_by": null
  },
  "requires_review": true,
  "review_gate": "HR_PRE"
}
```

---

### Approve Review Gate

```http
POST /api/v1/workflows/{workflow_id}/gates/{gate_id}/approve
Content-Type: application/json

{
  "gate_id": "HR_PRE",
  "approved_by": "human:jane.doe",
  "approved_artifacts": ["Concept Memo"],
  "metadata": {}
}
```

Approves a review gate and all specified artifacts (or all pending artifacts if `approved_artifacts` is omitted).

**Response:**
```json
{
  "gate_id": "HR_PRE",
  "state": "APPROVED",
  "approved_artifacts": ["Concept Memo"],
  "approved_at": "2026-01-20T12:00:00Z"
}
```

---

### Reject Review Gate

```http
POST /api/v1/workflows/{workflow_id}/gates/{gate_id}/reject
Content-Type: application/json

{
  "gate_id": "HR_PRE",
  "rejected_by": "human:jane.doe",
  "rejected_artifacts": ["Concept Memo"],
  "reason": "Content does not align with policy direction"
}
```

Rejects artifacts in a review gate.

**Response:**
```json
{
  "gate_id": "HR_PRE",
  "state": "REJECTED",
  "rejected_artifacts": ["Concept Memo"],
  "rejected_at": "2026-01-20T12:00:00Z"
}
```

---

## State Machine Overview

### Legislative States (Sequential)

1. **PRE_EVT** - Policy Opportunity Detected (Entry)
2. **INTRO_EVT** - Bill Vehicle Identified
3. **COMM_EVT** - Committee Referral
4. **FLOOR_EVT** - Floor Scheduled
5. **FINAL_EVT** - Vote Imminent
6. **IMPL_EVT** - Law Enacted (Terminal)

### Valid Transitions

- PRE_EVT → INTRO_EVT
- INTRO_EVT → COMM_EVT
- COMM_EVT → FLOOR_EVT
- FLOOR_EVT → FINAL_EVT
- FINAL_EVT → IMPL_EVT

**Invalid:**
- Any backward transition
- Any skip forward
- Terminal state exit (IMPL_EVT → any)

### Required Artifacts by State

See `AUTHORITATIVE_INVARIANTS.md` section 3 for complete list.

**PRE_EVT:**
- Stakeholder Landscape Map (required, no review)
- Concept Memo (required, HR_PRE review)

**INTRO_EVT:**
- Legitimacy & Policy Framing (required, HR_PRE review)
- Policy Whitepaper (required, HR_PRE review)

**COMM_EVT:**
- Committee Briefing Packets (required, HR_LANG review)
- Draft Legislative Language (required, HR_LANG review)
- Amendment Strategy (required, HR_LANG review)

**FLOOR_EVT:**
- Floor Messaging & Talking Points (required, HR_MSG review)
- Press & Media Narrative (required, HR_MSG review)

**FINAL_EVT:**
- Final Constituent Narrative (required, HR_RELEASE review)

**IMPL_EVT:**
- Implementation Guidance (required, no review)
- Outcome & Impact Report (required, no review)

---

### Check if Workflow Can Advance (Read-Only)

```http
GET /api/v1/workflows/{workflow_id}/can-advance
```

Returns a read-only check of internal readiness for state advancement. **Does NOT mutate state** and **does NOT require external confirmation**. Designed for UIs, dashboards, and agents to safely query readiness.

**Response (Ready):**
```json
{
  "can_advance": true,
  "blocking_issues": [],
  "current_state": "PRE_EVT",
  "next_state": "INTRO_EVT",
  "pending_gates": [],
  "missing_artifacts": []
}
```

**Response (Blocked):**
```json
{
  "can_advance": false,
  "blocking_issues": [
    "Missing required artifact: Concept Memo",
    "Review gate HR_PRE not approved"
  ],
  "current_state": "PRE_EVT",
  "next_state": "INTRO_EVT",
  "pending_gates": ["HR_PRE"],
  "missing_artifacts": ["Concept Memo", "Stakeholder Landscape Map"]
}
```

**Key Features:**
- ✅ **Read-only**: Never mutates workflow state
- ✅ **Deterministic**: Same input always produces same output
- ✅ **No external confirmation required**: Checks internal readiness only

---

### Explain Workflow State (Human-Readable)

```http
GET /api/v1/workflows/{workflow_id}/explain
```

Returns a human-readable explanation of workflow state and readiness. Designed for operators, dashboards, and downstream agents that need to understand status without making decisions.

**Response (Ready):**
```json
{
  "status": "ready",
  "summary": "Workflow is ready to advance from PRE_EVT to INTRO_EVT",
  "current_state": "PRE_EVT",
  "next_state": "INTRO_EVT",
  "explanation": "All required artifacts exist and are approved. All review gates are approved. Orchestrator is in active state.",
  "readiness_checks": {
    "artifacts_complete": true,
    "gates_approved": true,
    "orchestrator_active": true,
    "not_terminal": true
  },
  "blocking_reasons": [],
  "next_steps": [
    "Provide external confirmation: bill_vehicle_identified",
    "Call /advance endpoint to transition to INTRO_EVT"
  ]
}
```

**Response (Blocked):**
```json
{
  "status": "blocked",
  "summary": "Workflow cannot advance: 2 blocking issue(s) found",
  "current_state": "PRE_EVT",
  "next_state": "INTRO_EVT",
  "explanation": "Workflow is blocked from advancing. Missing required artifact(s): Concept Memo, Stakeholder Landscape Map. Review gate(s) not approved: HR_PRE.",
  "readiness_checks": {
    "artifacts_complete": false,
    "gates_approved": false,
    "orchestrator_active": true,
    "not_terminal": true
  },
  "blocking_reasons": [
    "Missing required artifact: Concept Memo",
    "Review gate HR_PRE not approved"
  ],
  "next_steps": [
    "Submit missing artifact: Concept Memo",
    "Submit missing artifact: Stakeholder Landscape Map",
    "Approve review gate HR_PRE",
    "Then check /can-advance again"
  ]
}
```

**Response (Terminal):**
```json
{
  "status": "terminal",
  "summary": "Workflow is in terminal state IMPL_EVT and cannot advance",
  "current_state": "IMPL_EVT",
  "next_state": null,
  "explanation": "The workflow has reached the terminal state IMPL_EVT (Law Enacted). No further state transitions are possible.",
  "readiness_checks": {
    "not_terminal": false,
    "artifacts_complete": true,
    "gates_approved": true,
    "orchestrator_active": true
  },
  "blocking_reasons": ["State is terminal"],
  "next_steps": ["Workflow is complete. No further actions needed."]
}
```

**Key Features:**
- ✅ **Read-only**: Never mutates workflow state
- ✅ **Human-readable**: Designed for operators and dashboards
- ✅ **Actionable**: Provides clear next steps
- ✅ **Deterministic**: Same input always produces same output

---

## Error Handling

All errors return structured responses with:
- `error_code`: Machine-readable error code
- `message`: Human-readable message
- `correlation_id`: Unique identifier for tracing
- `diagnostic_ids`: Associated diagnostic records (if any)

### Common Error Codes

- `WORKFLOW_NOT_FOUND` (404)
- `TRANSITION_VALIDATION_FAILED` (400)
- `MISSING_REQUIRED_ARTIFACT` (400)
- `REVIEW_GATE_NOT_APPROVED` (400)
- `MISSING_EXTERNAL_CONFIRMATION` (400)
- `ARTIFACT_VALIDATION_FAILED` (400)
- `INTERNAL_SERVER_ERROR` (500)

---

## Data Persistence

All data is persisted to disk in `agent-orchestrator/data/`:
- `workflows/{workflow_id}/state.json` - Workflow state
- `artifacts/{workflow_id}/{artifact_name}.json` - Artifact data
- `diagnostics/{workflow_id}.jsonl` - Diagnostic records (JSONL format)
- `logs/{workflow_id}.log` - Application logs

---

## Testing

Run tests:

```bash
cd agent-orchestrator
python -m pytest tests/ -v
```

---

## Zero Silent Failures Guarantee

The API guarantees:
- All validation failures produce diagnostic records
- All unexpected exceptions enter `ORCH_ERROR` state
- All errors include correlation IDs for tracing
- All state mutations are atomic (no partial updates)

---

## Quick Start: Happy Path Example

Complete workflow from creation to state advancement:

```bash
# Step 1: Create a new workflow
WORKFLOW_ID=$(curl -s -X POST http://localhost:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{"initial_state": "PRE_EVT"}' | jq -r '.workflow_id')

echo "Created workflow: $WORKFLOW_ID"

# Step 2: Check initial status
curl -s http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/status | jq '.'

# Step 3: Submit required artifacts
# Submit Stakeholder Landscape Map (no review required)
curl -s -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/artifacts \
  -H "Content-Type: application/json" \
  -d '{
    "artifact_name": "Stakeholder Landscape Map",
    "artifact_data": {
      "stakeholders": ["Industry A", "Industry B"],
      "analysis": "Key actors identified"
    }
  }' | jq '.'

# Submit Concept Memo (requires HR_PRE review)
curl -s -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/artifacts \
  -H "Content-Type: application/json" \
  -d '{
    "artifact_name": "Concept Memo",
    "artifact_data": {
      "title": "Policy Concept for Renewable Energy",
      "summary": "This memo outlines the policy direction...",
      "objectives": ["Reduce emissions", "Promote innovation"]
    },
    "requires_review": true,
    "review_gate": "HR_PRE"
  }' | jq '.'

# Step 4: Check status (should show pending gate)
curl -s http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/status | jq '{
  state: .legislative_state,
  can_advance: .can_advance,
  pending_gates: .pending_gates,
  blocking_issues: .blocking_issues
}'

# Step 5: Approve the review gate
curl -s -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/gates/HR_PRE/approve \
  -H "Content-Type: application/json" \
  -d '{
    "gate_id": "HR_PRE",
    "approved_by": "human:jane.doe",
    "approved_artifacts": ["Concept Memo"]
  }' | jq '.'

# Step 6: Advance state (with external confirmation)
curl -s -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/advance \
  -H "Content-Type: application/json" \
  -d '{
    "target_state": "INTRO_EVT",
    "external_confirmation": {
      "event_type": "bill_vehicle_identified",
      "confirmed_by": "human:jane.doe",
      "source_reference": "congress.gov/v3/bill/119/hr/1234",
      "metadata": {
        "bill_number": "HR-1234",
        "congress": 119
      }
    }
  }' | jq '.'

# Step 7: Verify new state
curl -s http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/status | jq '{
  state: .legislative_state,
  orchestrator_state: .orchestrator_state,
  can_advance: .can_advance
}'
```

## Example: Failure Case

What happens when you try to advance without required approvals:

```bash
# Create workflow
WORKFLOW_ID=$(curl -s -X POST http://localhost:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{"initial_state": "PRE_EVT"}' | jq -r '.workflow_id')

# Submit artifact but DON'T approve the gate
curl -s -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/artifacts \
  -H "Content-Type: application/json" \
  -d '{
    "artifact_name": "Concept Memo",
    "artifact_data": {"title": "Concept"},
    "requires_review": true,
    "review_gate": "HR_PRE"
  }' > /dev/null

# Try to advance (should fail with 400)
curl -s -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/advance \
  -H "Content-Type: application/json" \
  -d '{
    "target_state": "INTRO_EVT",
    "external_confirmation": {
      "event_type": "bill_vehicle_identified",
      "confirmed_by": "human:admin"
    }
  }' | jq '.'

# Expected response:
# {
#   "detail": {
#     "error_code": "TRANSITION_VALIDATION_FAILED",
#     "message": "Cannot advance from PRE_EVT to INTRO_EVT. 2 blocking issue(s) found.",
#     "blocking_issues": [
#       "Missing required artifact: Stakeholder Landscape Map",
#       "Artifact 'Concept Memo' not approved via HR_PRE"
#     ],
#     "correlation_id": "...",
#     "current_state": "PRE_EVT",
#     "target_state": "INTRO_EVT"
#   }
# }
```

## Example: Skip Forward (Invalid Transition)

```bash
# Create workflow in PRE_EVT
WORKFLOW_ID=$(curl -s -X POST http://localhost:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{"initial_state": "PRE_EVT"}' | jq -r '.workflow_id')

# Try to skip directly to COMM_EVT (should fail)
curl -s -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/advance \
  -H "Content-Type: application/json" \
  -d '{
    "target_state": "COMM_EVT",
    "external_confirmation": {
      "event_type": "committee_referral",
      "confirmed_by": "human:admin"
    }
  }' | jq '.detail.blocking_issues'

# Expected: ["Invalid transition: PRE_EVT -> COMM_EVT. Valid next state: INTRO_EVT"]
```

---

---

## Policy Artifacts (READ-ONLY CONTEXT)

The system includes a **Policy Artifacts** directory containing READ-ONLY POLICY CONTEXT for strategic planning and intelligence gathering.

### Location
- **Directory:** `agent-orchestrator/artifacts/policy/`
- **Status:** Canonical Policy Artifacts
- **Contract:** READ-ONLY POLICY CONTEXT (See `artifacts/policy/README.md`)

### Quick Access
- **Quick Reference:** [`artifacts/policy/QUICK_REFERENCE.md`](artifacts/policy/QUICK_REFERENCE.md)
- **Complete Index:** [`artifacts/policy/INDEX.md`](artifacts/policy/INDEX.md)
- **Agent Integration:** [`artifacts/policy/AGENT_INTEGRATION_GUIDE.md`](artifacts/policy/AGENT_INTEGRATION_GUIDE.md)

### Policy Documents
1. **`key_findings.md`** - Executive summary of policy analysis
2. **`stakeholder_map.md`** - Institutional stakeholder mapping
3. **`talking_points.md`** - Structured talking points
4. **`action_plan.md`** - 90-day execution roadmap
5. **`section_priority_table.md`** - Bill section mapping
6. **`staff_one_pager_p1.md`** - One-page brief
7. **`clear_ask_matrix_p1.md`** - Ask matrix

### Visual Diagrams
- **9 Mermaid diagrams** available in `artifacts/policy/diagrams/`
- **3 merged/comprehensive views** for overview
- **5 detailed views** for focused analysis
- **1 system context diagram** showing integration

### Usage Rules
- ✅ **Agents MAY:** Read policy artifacts as background context
- ✅ **Agents MAY:** Reference policy in analysis and drafts
- 🚫 **Agents MUST NOT:** Execute actions based on policy documents
- 🚫 **Agents MUST NOT:** Modify or overwrite policy files

**See:** [`artifacts/policy/README.md`](artifacts/policy/README.md) for complete contract documentation

---

## Production Considerations

1. **Security**: Configure CORS appropriately
2. **Authentication**: Add authentication middleware
3. **Rate Limiting**: Add rate limiting for production
4. **Backup**: Regularly backup `data/` directory
5. **Monitoring**: Monitor health endpoint and error rates
6. **Logging**: Configure structured logging to external service
7. **Database**: Consider migrating to database for high-scale deployments
