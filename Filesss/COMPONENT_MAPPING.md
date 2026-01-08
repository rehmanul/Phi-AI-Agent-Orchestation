# Component Mapping: Code to Master Diagram

**Master Diagram:** `.userInput/agent orchestrator 1.6.mmd`  
**Last Updated:** 2026-01-20

This document maps code components to elements in the master system architecture diagram.

---

## Legislative Spine → State Machine Implementation

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Legislative State Machine (PRE_EVT → IMPL_EVT) | `state/legislative-state.json` | Current state, state history, next allowed states |
| State Definitions | `AUTHORITATIVE_INVARIANTS.md` | Complete state definitions, transitions, entry/exit requirements |
| State Manager | `app/state_manager.py` | State transition logic, validation, persistence |
| State API | `app/routes.py` (state endpoints) | REST API for state queries and transitions |

**Validation:**
- States must match: PRE_EVT, INTRO_EVT, COMM_EVT, FLOOR_EVT, FINAL_EVT, IMPL_EVT
- Transitions must be sequential (no skipping)
- Terminal state (IMPL_EVT) cannot exit

---

## AI Service Layer → Code Modules

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Multi-Source Ingestion | `app/routes.py` (artifact submission) | API endpoints for artifact ingestion |
| Contextual Retrieval | `app/agent_client.py` | Agent context loading and retrieval |
| Feature Extraction | `app/agent_executor.py` | Agent execution and feature extraction |
| Draft & Strategy Generation | `agents/draft_*.py` | Drafting agents generate documents |
| Impact & Risk Scoring | `analysis/PRE_CONCEPT_RISK_ASSESSMENT.md` | Risk assessment analysis |

**Key Files:**
- `app/main.py` - FastAPI application entry point
- `app/routes.py` - Core API routes
- `app/agent_executor.py` - Agent execution engine
- `app/agent_client.py` - Agent client interface

---

## Human Review Gates → Review System

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| HR_PRE Gate | `review/HR_PRE_queue.json` | Pre-event review queue |
| HR_LANG Gate | `review/HR_LANG_queue.json` | Language review queue (if exists) |
| HR_MSG Gate | `review/HR_MSG_queue.json` | Messaging review queue (if exists) |
| HR_RELEASE Gate | `review/HR_RELEASE_queue.json` | Release review queue (if exists) |
| Review API | `app/routes.py` (review endpoints) | Approve/reject review gates |
| Review Sync | `app/review_sync.py` | Review queue synchronization |

**Validation:**
- All review gates must exist as queue files
- Review gates are non-negotiable (shown as decision diamonds in diagram)
- Human approval is required before state advancement

---

## Agent Types → Agent File Structure

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Intelligence Agents | `agents/intel_*.py` | Read-only analysis agents |
| Drafting Agents | `agents/draft_*.py` | Human-gated document generation |
| Execution Agents | `agents/execution_*.py` | Authorized action agents |
| Learning Agents | `agents/learning_*.py` | Post-execution analysis agents |
| Agent Spawner | `app/agent_spawner.py` | Agent lifecycle management |
| Agent Registry | `registry/agent-registry.json` | Active agent tracking |

**Agent File Naming Convention:**
- `{type}_{name}_{legislative_state}.py`
- Example: `intel_signal_scan_pre_evt.py`

**Agent Lifecycle States:**
- SPAWN → RUNNING → WAITING_REVIEW → TERMINATED
- Or: RUNNING → BLOCKED → RUNNING
- Or: RUNNING → MONITORING → TERMINATED

**Multi-Orchestrated Agent Categories:**

**Phase 1: Planning & Orchestration**
- `intel_strategy_align_pre_evt.py` - Strategy alignment to OKRs
- `execution_cloud_worker_comm_evt.py` - Cloud worker for heavy tasks

**Phase 2: Intelligence & Coalition**
- `intel_coalition_builder_intro_evt.py` - Internal stakeholder identification
- `intel_external_liaison_comm_evt.py` - External partner alignment
- `intel_policy_radar_comm_evt.py` - Regulatory monitoring
- `draft_legislator_comms_comm_evt.py` - Policymaker outreach drafting

**Phase 3: Grassroots Signal Processing**
- `agents/intel_grassroots/` - 12 agents (6 intake + 6 normalization)
- `agents/intel_escalation/` - 6 escalation mapping agents

**Phase 4: Coalition & Committee Intelligence**
- `agents/intel_coalition/` - 7 coalition density agents
- `agents/intel_committee/` - 6 committee targeting agents
- `agents/intel_sponsor/` - 5 sponsor pipeline agents

**Phase 5: Narrative & Vehicle Engineering**
- `agents/draft_narrative/` - 7 narrative construction agents
- `agents/draft_vehicle/` - 7 legislative vehicle engineering agents

**Phase 6: Risk & Counter-Narrative**
- `agents/intel_risk/` - 5 risk/counter-narrative agents

**Phase 7: Learning & Feedback**
- `agents/learning/` - 11 agents (5 post-launch + 6 operator cockpit)

---

## Memory & Learning → Data Storage Systems

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Evidence Store | `audit/audit-log.jsonl` | Audit log for all system events |
| Tactic Performance History | `registry/agent-registry.json` | Agent execution history and performance |
| Narrative Effectiveness Log | `artifacts/` (artifact metadata) | Artifact effectiveness tracking |
| Legislative Outcomes | `data/workflows/` | Workflow outcomes and results |
| Causal Attribution Engine | `agents/learning_*.py` | Learning agents analyze outcomes |

**Data Storage:**
- Audit log: JSONL format, append-only
- Registry: JSON format, agent state tracking
- Artifacts: JSON/Markdown, with `_meta` blocks

---

## Execution Loop → Execution Engine

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Strategy Decomposition | `execution/` (execution planning) | Execution strategy breakdown |
| Tactical Planning | `execution/` (tactical plans) | Tactical execution plans |
| Tactic Execution Engine | `app/execution_routes.py` | Execution API and engine |
| Live Monitoring | `monitoring/dashboard-terminal.py` | Real-time execution monitoring |
| Tactical Retuning | `execution/` (retuning logic) | Execution adjustment based on feedback |

**Execution Components:**
- `app/execution_routes.py` - Execution API endpoints
- `app/execution_tracker.py` - Execution tracking
- `execution/` directory - Execution scripts and plans
- `monitoring/` directory - Monitoring dashboards

---

## Campaign Operations → Campaign Modules

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Committee Outreach | `agents/execution_outreach_comm_evt.py` | Committee outreach execution |
| Narrative Reframing | `agents/draft_*.py` (framing agents) | Narrative reframing documents |
| Coalition Expansion | `agents/execution_coalition_comm_evt.py` | Coalition building execution |
| Opposition Neutralization | `agents/execution_counter_pressure_comm_evt.py` | Opposition counter-pressure |

**Campaign Agents:**
- Execution agents handle external actions
- Drafting agents create narrative materials
- Intelligence agents provide campaign intelligence

---

## Software Systems → Infrastructure Code

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Background Jobs | `app/agent_executor.py` | Agent execution as background tasks |
| Event Bus | `audit/audit-log.jsonl` | Event logging system |
| External APIs | `app/routes.py` | REST API endpoints |
| Observability | `monitoring/` | Dashboard and monitoring systems |

**Infrastructure:**
- FastAPI application: `app/main.py`
- Health monitoring: `app/health_monitor.py`
- Storage: `app/storage.py`
- Validation: `app/validator.py`

---

## Professional Service Field → Domain Knowledge

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Regulatory Affairs | `artifacts/` (regulatory artifacts) | Regulatory analysis documents |
| Legislative Policy | `artifacts/` (legislative artifacts) | Legislative policy documents |
| Compliance & Ethics | `guidance/PROFESSIONAL_GUIDANCE.json` | Professional guidance and ethics |
| Industry Expertise | `data/` (industry data) | Industry-specific data and analysis |
| Communications & Media | `agents/execution_media_comm_evt.py` | Media execution agents |

---

## Cursor Agent Interpretation Layer → Agent Rules

| Master Diagram Element | Code Location | Implementation Details |
|------------------------|---------------|----------------------|
| Diagram Reading & Topology Parsing | `MASTER_DIAGRAM_REFERENCE.md` | Master diagram reference |
| Legislative Spine Binding | `AUTHORITATIVE_INVARIANTS.md` | State machine definitions |
| Agent Role Identification | `agents/` (agent files) | Agent type and role definitions |
| Work Planning | `planning/` | Planning documents |
| Template Resolution | `agents/` (agent templates) | Agent output templates |

---

## Validation

Run component mapping validation:

```bash
python scripts/validate_component_mapping.py
```

This validates that all code components correctly map to master diagram elements.

---

## Maintenance

When adding new components:

1. **Map to Master:** Identify which master diagram element the component implements
2. **Update This Document:** Add entry to appropriate section
3. **Validate:** Run validation scripts to ensure alignment
4. **Update Diagram:** If new diagram element needed, update master diagram first

---

**Last Updated:** 2026-01-20  
**Status:** Active
