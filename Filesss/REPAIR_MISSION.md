# System Repair & Verification Mission

## STEP 0 — GOAL RESTATEMENT

### Overall GOAL

Fix critical gaps in the Risk Management Workflow System to enable frontend integration and ensure the 7-phase workflow can be executed end-to-end via API. Make the system safer, more usable, and properly expose all phase execution capabilities.

### Specific PROBLEMS Being Addressed

1. **Missing Phase Execution API Endpoints (Phases 2-7)**
   - Problem: Only Phase 1 (Intake) is exposed via API. Phases 2-7 have orchestrators but no API endpoints.
   - Impact: Frontend cannot trigger risk scan, modeling, ruin gates, judgment, or execution phases.

2. **No Workflow Phase Advancement Mechanism**
   - Problem: `WorkflowEngine.update_phase()` exists but no API endpoint to call it. No logic to advance from one phase to next.
   - Impact: Manual phase progression required, no automated workflow flow.

3. **Single Workflow Limitation**
   - Problem: `workflow_state.json` is a single file that overwrites. Cannot support multiple concurrent workflows.
   - Impact: Only one workflow can exist at a time, state is lost when starting new workflow.

4. **No Human Approval / Judgment Gate**
   - Problem: Judgment phase has no API endpoint. No mechanism to pause workflow for human review.
   - Impact: Cannot implement human-in-the-loop approval workflow.

5. **No Retry or Error Persistence**
   - Problem: Failed phases have no error state persistence. No retry mechanism.
   - Impact: Failures are lost, cannot recover from errors.

6. **No User-Visible Verification**
   - Problem: No way to verify system correctness or see what happened.
   - Impact: Users cannot trust the system or understand failures.

### What Will NOT Change

- ✅ Orchestrator logic (unless absolutely necessary)
- ✅ File-based JSON persistence (no database migration)
- ✅ Synchronous execution model (no background jobs)
- ✅ Existing Phase 1 API endpoints
- ✅ Agent implementations
- ✅ Schema definitions

---

## Execution Plan

Fixing problems one at a time, verifying each fix before proceeding.
