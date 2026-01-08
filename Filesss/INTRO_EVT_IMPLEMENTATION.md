# INTRO_EVT Phase Implementation

This document describes the implementation of the INTRO_EVT (Bill Vehicle Identified) phase agents and infrastructure.

## Overview

The INTRO_EVT phase implements the agent orchestration plan for when a bill vehicle has been identified. This phase focuses on:
- Intelligence gathering (signal scanning, stakeholder mapping, opposition detection)
- Drafting artifacts for human review (policy framing, whitepaper generation)

## Agents Implemented

### Intelligence Agents (Read-Only)

1. **intel_signal_scan_intro_evt.py** (`INT_SIGNAL_SCAN_001`)
   - Purpose: Scan signals from industry, courts, agencies, and media
   - Output: `artifacts/intel_signal_scan_intro_evt/signal_summary.json`
   - Risk Level: LOW
   - Termination: State advances to COMM_EVT OR explicit termination OR 30-day max

2. **intel_stakeholder_map_intro_evt.py** (`INT_STAKEHOLDER_MAP_001`)
   - Purpose: Build/update stakeholder map with sponsor alignment scores
   - Output: `artifacts/intel_stakeholder_map_intro_evt/PRE_STAKEHOLDER_MAP.json`
   - Risk Level: LOW
   - Termination: Map complete OR state advances to COMM_EVT OR explicit termination

3. **intel_opposition_detect_intro_evt.py** (`INT_OPPOSITION_DETECT_001`)
   - Purpose: Early detection of organized opposition and counter-narratives
   - Output: `artifacts/intel_opposition_detect_intro_evt/opposition_risk_assessment.json`
   - Risk Level: LOW
   - Termination: State advances to COMM_EVT OR explicit termination

### Drafting Agents (Human-Gated)

4. **draft_framing_intro_evt.py** (`DR_FRAMING_001`)
   - Purpose: Generate INTRO_FRAME artifact (Legitimacy & Policy Framing)
   - Output: `artifacts/draft_framing_intro_evt/INTRO_FRAME.json`
   - Risk Level: MEDIUM
   - Human Review: **REQUIRED** - HR_PRE (Approve Concept Direction)
   - Dependencies: Signal scan, stakeholder map, opposition assessment

5. **draft_whitepaper_intro_evt.py** (`DR_WHITEPAPER_001`)
   - Purpose: Generate INTRO_WHITEPAPER artifact for academic validation
   - Output: `artifacts/draft_whitepaper_intro_evt/INTRO_WHITEPAPER.json`
   - Risk Level: MEDIUM
   - Human Review: **REQUIRED** - HR_PRE (Approve Concept Direction)
   - Dependencies: Signal scan, stakeholder map (framing document optional)

## Orchestration

### Orchestration Script

**orchestrate_intro_evt.py** - Main orchestration script that:
1. Verifies monitoring dashboard is running
2. Checks legislative state is INTRO_EVT
3. Spawns intelligence agents first
4. Waits for intelligence artifacts
5. Spawns drafting agents
6. Reports on human review queue

### Execution Flow

```
1. Start monitoring dashboard (if not running)
   → python monitoring/dashboard-terminal.py

2. Verify state is INTRO_EVT
   → Check state/legislative-state.json

3. Run orchestration
   → python orchestrate_intro_evt.py

4. Review artifacts
   → Check review/HR_PRE_queue.json

5. Approve/reject via HR_PRE gate
   → Human authority required

6. After approval, advance to COMM_EVT
   → Human authority required (agents cannot advance state)
```

## State Management

- **Current State**: INTRO_EVT (Bill Vehicle Identified)
- **State Authority**: Legislative Spine (agents cannot advance state)
- **State Advancement**: Requires external reality or human confirmation
- **Next Allowed State**: COMM_EVT

## Human Review Gates

### HR_PRE (Approve Concept Direction)

**Triggers:**
- `DR_FRAMING_001` completes INTRO_FRAME draft
- `DR_WHITEPAPER_001` completes INTRO_WHITEPAPER draft

**Review Requirements:**
- Effort: ~10-15 minutes per artifact
- Risk Level: Low-Medium (directional alignment)
- Decision Authority: AVAQ Strategic Team

**Blocking Behavior:**
- Drafting agents enter `WAITING_REVIEW` status
- No state advancement until approval
- Artifacts remain in draft state

## Monitoring

The monitoring dashboard (`monitoring/dashboard-terminal.py`) displays:
- Overall system status
- Legislative state cursor
- Pending approvals count
- Agent status (RUNNING / IDLE / BLOCKED / WAITING_REVIEW / FAILED / RETIRED)
- Task queue status
- Recent events

**Dashboard must be running before agent spawn** (per override rules).

## Agent Registry

All agents register themselves in `registry/agent-registry.json` with:
- Agent ID and type
- Status and current task
- Scope and termination condition
- Risk level
- Output artifacts
- Heartbeat timestamps

## Audit Trail

All agent actions are logged to `audit/audit-log.jsonl` with:
- Timestamp
- Event type (agent_spawned, task_started, task_completed, etc.)
- Agent ID
- Message and metadata

## Compliance

This implementation complies with:
- ✅ Legislative Spine Authority (INTRO_EVT is authoritative state)
- ✅ Agent Orchestration Model (ephemeral, task-bounded, state-bounded)
- ✅ Human-in-the-Loop (drafting outputs require HR_PRE approval)
- ✅ Professional Boundaries (agents operate within GUIDANCE constraints)
- ✅ Memory Integration (agents read/write to memory stores)
- ✅ Monitoring Override (dashboard must be active before execution)

## Files Created

### Agent Scripts
- `agents/intel_signal_scan_intro_evt.py`
- `agents/intel_stakeholder_map_intro_evt.py`
- `agents/intel_opposition_detect_intro_evt.py`
- `agents/draft_framing_intro_evt.py`
- `agents/draft_whitepaper_intro_evt.py`

### Orchestration
- `orchestrate_intro_evt.py`

### Documentation
- `INTRO_EVT_IMPLEMENTATION.md` (this file)

## Next Steps

After INTRO_EVT phase completion:
1. Human review of INTRO_FRAME and INTRO_WHITEPAPER via HR_PRE
2. Human authority advances state to COMM_EVT
3. COMM_EVT agents can then be spawned (drafting + execution agents)

## Notes

- All agents follow the same pattern as PRE_EVT agents
- Agents check for GUIDANCE signatures (proceed in TEST_MODE if unsigned)
- Intelligence agents are read-only (no external actions)
- Drafting agents require human approval before artifacts are finalized
- State advancement is always human-controlled (agents cannot advance state)
