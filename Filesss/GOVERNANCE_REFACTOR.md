# Governance Refactor - Execution Planning vs External Release

**Date:** 2026-01-07  
**Status:** ✅ COMPLETE  
**Authority:** System Instruction - Authoritative

---

## Objective

Remove human approval requirements for the **CREATION and EXECUTION** of agentic workflows, while **STRICTLY preserving** human review gates for ALL externally expressive artifacts.

---

## New Governance Rules

### 1. AGENTIC WORKFLOW CREATION (FREE)

Agents MAY autonomously:
- Generate execution plans
- Spawn execution workflows
- Identify targets, stakeholders, and execution paths
- Submit execution intents
- Queue execution requests
- Simulate/dry-run executions

**NO HR_* gate may block workflow creation or execution intent.**

### 2. EXECUTION VS RELEASE SEPARATION

**Execution intent ≠ External release**

- Execution agents may prepare, queue, and simulate actions
- NO outbound communication, publication, or external signaling may occur without artifact approval
- Dry-run and simulation are always allowed
- Actual external communication requires approved language artifacts

### 3. HUMAN REVIEW SCOPE (MANDATORY FOR EXTERNAL RELEASE)

Human approval is **REQUIRED ONLY** for:
- Language artifacts (legislative language, briefing packets)
- Messaging artifacts (floor messaging, media narratives)
- Outreach copy (email content based on language artifacts)
- Policy documents
- **Any content that leaves the system boundary**

These artifacts MUST pass through:
- **HR_LANG** (language artifacts)
- **HR_MSG** (messaging artifacts)
- **HR_RELEASE** (final release)

### 4. HR_LANG CLARIFICATION

**HR_LANG applies ONLY to drafted language content.**

HR_LANG **MUST NOT** block:
- Execution planning
- Target selection
- Workflow orchestration
- Non-expressive metadata
- Dry-run simulation

### 5. SAFE DEFAULTS

If an execution workflow reaches a point where external communication would occur:
- Automatically pause
- Generate required artifacts (if missing)
- Route artifacts to human review
- Resume ONLY after approval

### 6. STATE ADVANCEMENT

- Workflow state MAY advance through planning and execution phases without human approval
- Legislative or external state transitions require approved artifacts (unchanged)

---

## Implementation Changes

### Execution Agents

**Before:**
- Created execution requests with `review_gate="HR_LANG"`
- Set `requires_approval=True`
- Submitted to approval manager
- Blocked until human approval

**After:**
- Create execution requests with `review_gate=None`
- Set `requires_approval=False`
- Track source artifact in metadata
- Execute immediately (dry-run) or check approval at send time

### Email Provider

**Before:**
- No approval checking at send time
- All blocking happened at request creation

**After:**
- Check source artifact approval before actual send (not dry-run)
- Allow dry-run simulation without approval
- Block actual SMTP send if source artifact not approved

### Approval Manager

**Before:**
- Mapped execution requests to review gates
- Required approval before request creation

**After:**
- Retained for backward compatibility
- Approval happens at artifact level (not request level)
- Execution planning doesn't use approval manager

---

## Code Changes

### Files Modified

1. **agent-orchestrator/agents/execution_outreach_comm_evt.py**
   - Removed `review_gate="HR_LANG"` from request creation
   - Removed approval submission
   - Added source artifact tracking
   - Changed status from "PENDING_APPROVAL" to "PLANNED"

2. **agent-orchestrator/execution/email_provider.py**
   - Added `_check_artifact_approval()` method
   - Check approval before actual send (not dry-run)
   - Block actual SMTP send if artifact not approved

3. **agent-orchestrator/execution/approval_manager.py**
   - Updated docstring to clarify new governance
   - Approval now happens at artifact level

4. **agent-orchestrator/agents/execution_coalition_comm_evt.py**
   - Updated status from "BLOCKED" to "IDLE"
   - Updated governance language

5. **agent-orchestrator/agents/execution_media_comm_evt.py**
   - Updated status from "BLOCKED" to "IDLE"
   - Updated governance language

6. **agent-orchestrator/agents/execution_counter_pressure_comm_evt.py**
   - Updated status from "BLOCKED" to "IDLE"
   - Updated governance language

---

## Expected Outcomes

✅ **No execution deadlocks** due to premature HR_* gating  
✅ **Intelligence and learning loops** operate on real executions  
✅ **Humans review WHAT IS SAID**, not THAT something is attempted  
✅ **System moves forward** while preserving accountability  
✅ **Dry-run and simulation** always available  
✅ **Actual external communication** protected by artifact approval

---

## Verification

### Test Execution Agent

```bash
python agent-orchestrator/agents/execution_outreach_comm_evt.py
```

**Expected:**
- Creates execution requests without blocking
- Executes in dry-run mode immediately
- Logs execution requests for monitoring
- Status: "PLANNED" or "COMPLETED" (not "PENDING_APPROVAL")

### Test Approval Check

When actual send is attempted (DRY_RUN_MODE=False):
- Email provider checks source artifact approval
- Blocks if artifact status != "ACTIONABLE"
- Allows if artifact approved

---

## Backward Compatibility

- Approval manager retained (for future use or backward compatibility)
- Existing approval queue structure unchanged
- Review gates still work for language artifacts
- State advancement rules unchanged (still require approved artifacts)

---

**This instruction overrides any prior conflicting rules.**
