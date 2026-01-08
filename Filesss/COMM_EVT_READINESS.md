# COMM_EVT Readiness Assessment

**Current State:** COMM_EVT (Committee Referral)  
**Date:** 2026-01-20  
**Status:** ⏳ READY FOR ARTIFACT GENERATION

---

## State Advancement Complete

✅ **State:** Advanced from INTRO_EVT to COMM_EVT  
✅ **Review Gate:** HR_LANG active and ready  
✅ **Next State:** FLOOR_EVT (requires HR_LANG approvals)

---

## Required Artifacts Status

### Required for COMM_EVT → FLOOR_EVT

1. **Committee Briefing Packets** ⏳
   - Agent: `draft_committee_briefing_comm_evt.py`
   - Status: Check if exists/generated
   - Review Gate: HR_LANG

2. **Draft Legislative Language** ⏳
   - Agent: `draft_legislative_language_comm_evt.py`
   - Status: Check if exists/generated
   - Review Gate: HR_LANG

3. **Amendment Strategy** ⏳
   - Agent: `draft_amendment_strategy_comm_evt.py`
   - Status: Check if exists/generated
   - Review Gate: HR_LANG

### Optional

4. **Committee Agenda & Member Analysis** (Optional)
   - Agent: Intelligence agent
   - Status: Optional

---

## Review Gate Status

**HR_LANG** (Legislative Language Review)
- Status: NOT_STARTED (placeholder ready)
- Display Name: "Legislative Language Review"
- Description: "Human approval of drafted legislative text before committee activity"
- Ready for: Artifact submissions

---

## Next Actions

### Option 1: Generate COMM_EVT Artifacts (Recommended)

**Spawn drafting agents to generate required artifacts:**

1. Run `draft_committee_briefing_comm_evt.py`
2. Run `draft_legislative_language_comm_evt.py`
3. Run `draft_amendment_strategy_comm_evt.py`

**After generation:**
- Artifacts will be submitted to HR_LANG queue
- Await human approval
- Once approved + external event (floor scheduling), advance to FLOOR_EVT

### Option 2: Check Existing Artifacts

**Check if artifacts already exist:**
- `artifacts/comm_evt/` directory
- `artifacts/draft_committee_briefing_comm_evt/`
- `artifacts/draft_legislative_language_comm_evt/`
- `artifacts/draft_amendment_strategy_comm_evt/`

If artifacts exist but not in queue, submit them to HR_LANG.

---

## State Advancement Requirements (Future)

**To advance from COMM_EVT → FLOOR_EVT:**
1. ⏳ Legislative Language approved via HR_LANG
2. ⏳ Amendment Strategy approved via HR_LANG
3. ⏳ Committee Briefing Packets approved via HR_LANG
4. ⏳ External confirmation: Floor scheduling

---

**Last Updated:** 2026-01-20  
**Status:** Ready for COMM_EVT artifact generation
