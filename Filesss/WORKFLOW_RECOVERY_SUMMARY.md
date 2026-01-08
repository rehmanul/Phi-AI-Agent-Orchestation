# Workflow Recovery Summary

## Problem
The `orchestrator_core_planner` workflow was reported as "down" and needed to be reactivated.

## Solution Implemented

### 1. Added Recovery Endpoint
- **File**: `agent-orchestrator/app/routes.py`
- **Endpoint**: `POST /api/v1/workflows/{workflow_id}/recover`
- **Function**: Manually recover workflows from `ORCH_ERROR` state to `ORCH_IDLE`
- **Safety**: Only works if workflow is in `ORCH_ERROR` state

### 2. Created Recovery Scripts
- **File**: `agent-orchestrator/scripts/fix_workflow.py`
  - Check workflow status via API or direct storage
  - Recover workflows from error state
  - List all workflows
  - Usage: `python scripts/fix_workflow.py <workflow_id> [--recover] [--direct]`

- **File**: `agent-orchestrator/scripts/setup_orchestrator_core_planner.py`
  - Setup or recover the `orchestrator_core_planner` workflow
  - Creates workflow if it doesn't exist
  - Recovers from `ORCH_ERROR` if needed
  - Usage: `python scripts/setup_orchestrator_core_planner.py`

### 3. Workflow Status
- **Workflow ID**: `orchestrator_core_planner`
- **Legislative State**: `PRE_EVT`
- **Orchestrator State**: `ORCH_IDLE` ✅
- **Status**: **ACTIVE AND READY**

## How to Use

### Check Workflow Status
```bash
# Via API (if server is running)
python scripts/fix_workflow.py orchestrator_core_planner

# Direct storage access
python scripts/fix_workflow.py orchestrator_core_planner --direct
```

### Recover Workflow from Error
```bash
# Via API
python scripts/fix_workflow.py orchestrator_core_planner --recover

# Direct storage access
python scripts/fix_workflow.py orchestrator_core_planner --recover --direct

# Or use the setup script
python scripts/setup_orchestrator_core_planner.py
```

### Via API Endpoint
```bash
# Check status
curl http://localhost:8000/api/v1/workflows/orchestrator_core_planner/status

# Recover from error
curl -X POST http://localhost:8000/api/v1/workflows/orchestrator_core_planner/recover
```

## Current State
✅ Workflow exists and is active
✅ Orchestrator state: `ORCH_IDLE` (ready to proceed)
✅ No blocking errors
✅ Can advance when requirements are met

## Next Steps
The workflow is ready to:
1. Accept artifact submissions
2. Advance to next legislative state when requirements are met
3. Spawn agents for the current state (PRE_EVT)

## Notes
- The workflow was created if it didn't exist
- If it was in `ORCH_ERROR` state, it has been recovered to `ORCH_IDLE`
- The recovery endpoint adds a diagnostic record for audit trail
- All state changes are logged in the workflow's state history
