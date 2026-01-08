# Agent Orchestrator — Authoritative Invariants

**Version:** 1.0.0  
**Authority:** System Definition (Derived from Legislative Spine)  
**Last Updated:** 2026-01-20

---

## Master System Architecture Diagram

**Authoritative Source:** `.userInput/agent orchestrator 1.6.mmd`

This document defines the authoritative invariants for the Agent Orchestrator system. These invariants are derived from and must align with the master system architecture diagram located at `.userInput/agent orchestrator 1.6.mmd` (939 lines).

The master diagram shows the complete system architecture including:
- Legislative Process Spine (PRE_EVT → IMPL_EVT)
- AI Service Execution Layer
- Human Review Gates (HR_PRE, HR_LANG, HR_MSG, HR_RELEASE)
- Memory & Learning Systems
- Execution Loop
- Agent Orchestration Model
- Campaign Operations
- Software Systems

All system components, state machines, and agent behaviors defined in this document must align with the master diagram. For detailed component mappings, see `COMPONENT_MAPPING.md`.

**Reference:** See `MASTER_DIAGRAM_REFERENCE.md` for complete master diagram documentation.

---

## 1. Complete State Machine

### 1.1 Primary Legislative States

| State ID | State Name | Definition | Type |
|----------|------------|------------|------|
| `PRE_EVT` | Policy Opportunity Detected | External signal detected (election, court, agency, market) | Entry State |
| `INTRO_EVT` | Bill Vehicle Identified | Legislative vehicle exists for policy | Intermediate |
| `COMM_EVT` | Committee Referral | Bill assigned to committee(s) | Intermediate |
| `FLOOR_EVT` | Floor Scheduled | Bill scheduled for floor consideration | Intermediate |
| `FINAL_EVT` | Vote Imminent | Final vote scheduled/occurring | Intermediate |
| `IMPL_EVT` | Law Enacted | Bill becomes law | Terminal State |

### 1.2 System States

| State ID | State Name | Purpose |
|----------|------------|---------|
| `ORCH_IDLE` | Orchestrator Idle | No active work, waiting for state change |
| `ORCH_ACTIVE` | Orchestrator Active | Agents spawned and executing |
| `ORCH_PAUSED` | Orchestrator Paused | Human-initiated pause |
| `ORCH_ERROR` | Orchestrator Error | System error requiring intervention |

### 1.3 Agent Lifecycle States

| State | Description | Transition Rules |
|-------|-------------|------------------|
| `SPAWN` | Agent instantiated by orchestrator | Orchestrator spawns based on state |
| `RUNNING` | Agent actively executing task | Normal operation |
| `WAITING_REVIEW` | Agent output pending human approval | Drafting/Execution agent blocked |
| `BLOCKED` | Agent cannot proceed (dependency missing) | External dependency |
| `MONITORING` | Agent in observation mode | Execution agents during monitoring phase |
| `TERMINATED` | Agent completed and retired | Normal completion or forced termination |
| `FAILED` | Agent error state | Must be logged and audited |

---

## 2. Valid State Transitions

### 2.1 Legislative State Transitions (Linear Path)

| From State | To State | Transition Type | Authority |
|------------|----------|-----------------|-----------|
| `PRE_EVT` | `INTRO_EVT` | Sequential | Human Approval + External Confirmation |
| `INTRO_EVT` | `COMM_EVT` | Sequential | Human Approval (HR_PRE) + External Confirmation |
| `COMM_EVT` | `FLOOR_EVT` | Sequential | Human Approval (HR_LANG) + External Confirmation |
| `FLOOR_EVT` | `FINAL_EVT` | Sequential | Human Approval (HR_MSG) + External Confirmation |
| `FINAL_EVT` | `IMPL_EVT` | Sequential | Human Approval (HR_RELEASE) + External Confirmation |

### 2.2 Invalid Legislative State Transitions

| Invalid Transition | Reason |
|-------------------|--------|
| Any skip forward (e.g., `PRE_EVT` → `COMM_EVT`) | States must be traversed sequentially |
| Any backward transition (e.g., `COMM_EVT` → `INTRO_EVT`) | Legislative process is unidirectional |
| Self-loops (e.g., `COMM_EVT` → `COMM_EVT`) | State changes require external events |
| Terminal state exit (`IMPL_EVT` → any) | `IMPL_EVT` is terminal |

### 2.3 Orchestrator State Transitions

| From State | To State | Trigger |
|------------|----------|---------|
| `ORCH_IDLE` | `ORCH_ACTIVE` | Legislative state change to active phase |
| `ORCH_ACTIVE` | `ORCH_IDLE` | All agents terminated, no pending work |
| `ORCH_ACTIVE` | `ORCH_PAUSED` | Human pause command |
| `ORCH_PAUSED` | `ORCH_ACTIVE` | Human resume command |
| `ORCH_ACTIVE` | `ORCH_ERROR` | System error detected |
| `ORCH_ERROR` | `ORCH_IDLE` | Error resolved by human |

### 2.4 Agent Lifecycle Transitions

| From State | To State | Trigger | Constraints |
|------------|----------|---------|-------------|
| — | `SPAWN` | Orchestrator spawn command | Must match state eligibility |
| `SPAWN` | `RUNNING` | Agent initialization complete | All inputs validated |
| `RUNNING` | `WAITING_REVIEW` | Drafting/Execution agent produces output | Automatic for gated agents |
| `WAITING_REVIEW` | `RUNNING` | Human approval received | Approval logged |
| `WAITING_REVIEW` | `TERMINATED` | Human rejection | Output discarded |
| `RUNNING` | `MONITORING` | Execution agent enters monitoring phase | Execution agents only |
| `MONITORING` | `RUNNING` | Alert/retune triggered | Back to execution |
| `RUNNING` | `BLOCKED` | Dependency missing | Auto-retry or terminate |
| `BLOCKED` | `RUNNING` | Dependency satisfied | Resume execution |
| `RUNNING` | `TERMINATED` | Task completion | Normal exit |
| `RUNNING` | `FAILED` | Error exception | Must be logged |
| `FAILED` | `TERMINATED` | Human intervention | Cannot auto-recover |
| `MONITORING` | `TERMINATED` | Scope completion | Normal exit |
| Any | `TERMINATED` | Orchestrator force-terminate | Human command or rule violation |

---

## 3. Required Artifacts Per State

### 3.1 PRE_EVT Artifacts

| Artifact Name | Required | Produced By | Purpose | Human Review |
|---------------|----------|-------------|---------|--------------|
| Stakeholder Landscape Map | Required | Intelligence Agent | Identify key actors | No |
| Concept Memo | Required | Drafting Agent | Directional alignment | HR_PRE (Required) |
| Signal Scan Report | Optional | Intelligence Agent | External signals | No |

**State Entry Requirements:**
- External signal detected (election, court, agency, market)

**State Exit Requirements:**
- Concept Memo approved via HR_PRE
- External confirmation of bill vehicle identification

---

### 3.2 INTRO_EVT Artifacts

| Artifact Name | Required | Produced By | Purpose | Human Review |
|---------------|----------|-------------|---------|--------------|
| Legitimacy & Policy Framing | Required | Drafting Agent | Narrative foundation | HR_PRE (Required) |
| Policy Whitepaper | Required | Drafting Agent | Academic validation | HR_PRE (Required) |
| Sponsor Targeting Analysis | Optional | Intelligence Agent | Identify champions | No |

**State Entry Requirements:**
- Concept Memo approved (HR_PRE)
- Bill vehicle identified (external confirmation)

**State Exit Requirements:**
- Policy Framing approved via HR_PRE
- Policy Whitepaper approved via HR_PRE
- External confirmation of committee referral

---

### 3.3 COMM_EVT Artifacts

| Artifact Name | Required | Produced By | Purpose | Human Review |
|---------------|----------|-------------|---------|--------------|
| Committee Briefing Packets | Required | Drafting Agent | Staff education | HR_LANG (Required) |
| Draft Legislative Language | Required | Drafting Agent | Statutory text | HR_LANG (Required) |
| Amendment Strategy | Required | Drafting Agent | Tactical options | HR_LANG (Required) |
| Committee Agenda & Member Analysis | Optional | Intelligence Agent | Vote prediction | No |

**State Entry Requirements:**
- Policy Framing approved
- Policy Whitepaper approved
- External confirmation of committee referral

**State Exit Requirements:**
- Legislative Language approved via HR_LANG
- Amendment Strategy approved via HR_LANG
- External confirmation of floor scheduling

---

### 3.4 FLOOR_EVT Artifacts

| Artifact Name | Required | Produced By | Purpose | Human Review |
|---------------|----------|-------------|---------|--------------|
| Floor Messaging & Talking Points | Required | Drafting Agent | Member communication | HR_MSG (Required) |
| Press & Media Narrative | Required | Drafting Agent | Public messaging | HR_MSG (Required) |
| Timing & Vote Whip Strategy | Optional | Execution Agent | Tactical execution | HR_MSG (Required) |

**State Entry Requirements:**
- Legislative Language approved
- Amendment Strategy approved
- External confirmation of floor scheduling

**State Exit Requirements:**
- Floor Messaging approved via HR_MSG
- Media Narrative approved via HR_MSG
- External confirmation of vote scheduling

---

### 3.5 FINAL_EVT Artifacts

| Artifact Name | Required | Produced By | Purpose | Human Review |
|---------------|----------|-------------|---------|--------------|
| Final Constituent Narrative | Required | Drafting Agent | Public release | HR_RELEASE (Required) |
| Coalition Activation Plan | Optional | Execution Agent | Partner mobilization | HR_RELEASE (Required) |

**State Entry Requirements:**
- Floor Messaging approved
- Media Narrative approved
- External confirmation of vote scheduling

**State Exit Requirements:**
- Final Narrative approved via HR_RELEASE
- External confirmation of law enactment

---

### 3.6 IMPL_EVT Artifacts

| Artifact Name | Required | Produced By | Purpose | Human Review |
|---------------|----------|-------------|---------|--------------|
| Implementation Guidance | Required | Drafting Agent | Post-enactment plan | No |
| Outcome & Impact Report | Required | Learning Agent | Post-mortem analysis | No |
| Oversight & Compliance Prep | Optional | Drafting Agent | Regulatory readiness | No |

**State Entry Requirements:**
- Final Narrative approved
- External confirmation of law enactment

**State Exit Requirements:**
- N/A (Terminal State)

---

## 4. Preconditions for State Advancement

### 4.1 PRE_EVT → INTRO_EVT

**Required Preconditions:**
1. ✅ Concept Memo exists and is approved via HR_PRE
2. ✅ External confirmation: Bill vehicle identified (external event)
3. ✅ Orchestrator state: `ORCH_ACTIVE` or `ORCH_IDLE`
4. ✅ No blocking errors in agent execution

**Human Review Gates:**
- HR_PRE: Concept Memo approval (required)
  - Estimated review time: 10-15 minutes
  - Risk level: Low-Medium (directional alignment)

**External Confirmations:**
- Bill vehicle identified (legislative action)

**Invalid Advance Scenarios:**
- ❌ Concept Memo not approved
- ❌ No external confirmation of bill vehicle
- ❌ Orchestrator in `ORCH_ERROR` state
- ❌ Critical agent in `FAILED` state

---

### 4.2 INTRO_EVT → COMM_EVT

**Required Preconditions:**
1. ✅ Legitimacy & Policy Framing artifact exists and is approved via HR_PRE
2. ✅ Policy Whitepaper exists and is approved via HR_PRE
3. ✅ External confirmation: Committee referral occurred (external event)
4. ✅ All required PRE_EVT artifacts completed
5. ✅ Orchestrator state: `ORCH_ACTIVE` or `ORCH_IDLE`

**Human Review Gates:**
- HR_PRE: Policy Framing approval (required)
- HR_PRE: Policy Whitepaper approval (required)

**External Confirmations:**
- Committee referral (legislative action)

**Invalid Advance Scenarios:**
- ❌ Policy Framing not approved
- ❌ Policy Whitepaper not approved
- ❌ No external confirmation of committee referral
- ❌ Any PRE_EVT artifacts missing

---

### 4.3 COMM_EVT → FLOOR_EVT

**Required Preconditions:**
1. ✅ Draft Legislative Language exists and is approved via HR_LANG
2. ✅ Amendment Strategy exists and is approved via HR_LANG
3. ✅ Committee Briefing Packets exist and are approved via HR_LANG
4. ✅ External confirmation: Floor scheduling occurred (external event)
5. ✅ All required INTRO_EVT artifacts completed
6. ✅ Orchestrator state: `ORCH_ACTIVE` or `ORCH_IDLE`

**Human Review Gates:**
- HR_LANG: Legislative Language approval (required)
  - Estimated review time: 45-90 minutes
  - Risk level: High (statutory/legal exposure)
- HR_LANG: Amendment Strategy approval (required)
- HR_LANG: Committee Briefing Packets approval (required)

**External Confirmations:**
- Floor scheduling (legislative action)

**Invalid Advance Scenarios:**
- ❌ Legislative Language not approved
- ❌ Amendment Strategy not approved
- ❌ Committee Briefing Packets not approved
- ❌ No external confirmation of floor scheduling
- ❌ Any INTRO_EVT artifacts missing

---

### 4.4 FLOOR_EVT → FINAL_EVT

**Required Preconditions:**
1. ✅ Floor Messaging & Talking Points exists and is approved via HR_MSG
2. ✅ Press & Media Narrative exists and is approved via HR_MSG
3. ✅ Timing & Vote Whip Strategy exists and is approved via HR_MSG (if created)
4. ✅ External confirmation: Vote scheduling occurred (external event)
5. ✅ All required COMM_EVT artifacts completed
6. ✅ Orchestrator state: `ORCH_ACTIVE` or `ORCH_IDLE`

**Human Review Gates:**
- HR_MSG: Floor Messaging approval (required)
  - Estimated review time: 15-30 minutes
  - Risk level: Medium (reputational/narrative)
- HR_MSG: Media Narrative approval (required)

**External Confirmations:**
- Vote scheduling (legislative action)

**Invalid Advance Scenarios:**
- ❌ Floor Messaging not approved
- ❌ Media Narrative not approved
- ❌ No external confirmation of vote scheduling
- ❌ Any COMM_EVT artifacts missing

---

### 4.5 FINAL_EVT → IMPL_EVT

**Required Preconditions:**
1. ✅ Final Constituent Narrative exists and is approved via HR_RELEASE
2. ✅ Coalition Activation Plan exists and is approved via HR_RELEASE (if created)
3. ✅ External confirmation: Law enactment occurred (external event)
4. ✅ All required FLOOR_EVT artifacts completed
5. ✅ Orchestrator state: `ORCH_ACTIVE` or `ORCH_IDLE`

**Human Review Gates:**
- HR_RELEASE: Final Narrative approval (required)
  - Estimated review time: 5-10 minutes
  - Risk level: High Visibility (irreversible action)

**External Confirmations:**
- Law enactment (legislative action)

**Invalid Advance Scenarios:**
- ❌ Final Narrative not approved
- ❌ No external confirmation of law enactment
- ❌ Any FLOOR_EVT artifacts missing

---

## 5. Agent Eligibility by State

### 5.1 State-to-Agent Mapping

| Legislative State | Eligible Agent Types | Spawnable Agents |
|-------------------|---------------------|------------------|
| `PRE_EVT` | Intelligence, Drafting | Signal Scan, Stakeholder Mapping, Concept Memo |
| `INTRO_EVT` | Intelligence, Drafting | Policy Framing, Whitepaper, Sponsor Targeting |
| `COMM_EVT` | Intelligence, Drafting, Execution | Committee Briefing, Legislative Language, Amendment Strategy, Outreach Execution |
| `FLOOR_EVT` | Intelligence, Drafting, Execution, Monitoring | Floor Messaging, Media Narrative, Coalition Activation, Media Seeding |
| `FINAL_EVT` | Execution, Monitoring | Coalition Activation, Counter-Pressure, Final Narrative |
| `IMPL_EVT` | Learning Only | Outcome Attribution, Tactic Performance, Narrative Effectiveness |

### 5.2 Agent Spawn Rules

**Rule 1: State-Bounded Eligibility**
- Agents may only be spawned if current legislative state permits their type
- Violation: Immediate termination of spawned agent

**Rule 2: Scope Definition Required**
- Every spawned agent must have explicit:
  - Purpose
  - Scope boundaries
  - Inputs
  - Outputs
  - Termination condition

**Rule 3: Ephemeral Lifetime**
- No agent persists beyond its scope
- Agents terminate when:
  - Task complete
  - State advances beyond eligibility
  - Scope completion
  - Error occurs

---

## 6. Hard Safety Constraints

### 6.1 Non-Negotiable Agent Rules

| Rule ID | Rule Statement | Violation Consequence |
|---------|---------------|----------------------|
| RULE_1 | No agent may advance legislative state | Immediate termination + audit log |
| RULE_2 | No agent may self-release public outputs | Output blocked + agent terminated |
| RULE_3 | No agent persists beyond its scope | Forced termination by orchestrator |
| RULE_4 | No agent may bypass human review gates | Output blocked + violation logged |
| RULE_5 | No agent may operate outside defined scope | Immediate termination |

### 6.2 Orchestrator Constraints

| Constraint | Description | Enforcement |
|-----------|-------------|-------------|
| State Authority | Only external events or human confirmation may advance state | Orchestrator blocks state changes |
| Agent Spawn Limits | Maximum concurrent agents per type | Configurable limit enforcement |
| Review Gate Blocking | No advancement past review gate without approval | State machine enforces blocking |
| Memory Override Prevention | Memory never overrides state, human judgment, or governance | Architecture constraint |

---

## 7. Human Review Gate Definitions

### 7.1 Review Gate Catalog

| Gate ID | Gate Name | Triggers For | Required Artifacts | Time Estimate | Risk Level |
|---------|-----------|-------------|-------------------|---------------|------------|
| HR_PRE | Concept Direction Approval | PRE_EVT → INTRO_EVT, INTRO_EVT → COMM_EVT | Concept Memo, Policy Framing, Whitepaper | 10-90 min | Low-Medium |
| HR_LANG | Legislative Language Approval | COMM_EVT → FLOOR_EVT | Legislative Language, Amendment Strategy, Briefing Packets | 45-90 min | High |
| HR_MSG | Messaging & Narrative Approval | FLOOR_EVT → FINAL_EVT | Floor Messaging, Media Narrative | 15-30 min | Medium |
| HR_RELEASE | Public Release Authorization | FINAL_EVT → IMPL_EVT | Final Narrative, Coalition Plan | 5-10 min | High Visibility |

### 7.2 Review Gate Behavior

**Gate States:**
- `PENDING`: Artifact submitted, awaiting human review
- `APPROVED`: Human approval granted, logged
- `REJECTED`: Human rejection, artifact discarded
- `REVISED`: Agent revised artifact after rejection

**Gate Blocking:**
- State advancement blocked until all required gates are `APPROVED`
- Multiple gates may be pending simultaneously
- Gates are state-specific (e.g., HR_PRE at PRE_EVT differs from HR_PRE at INTRO_EVT)

---

## 8. External Event Requirements

### 8.1 External Confirmation Types

| Event Type | Confirmation Source | Required For Transition |
|-----------|-------------------|------------------------|
| Bill Vehicle Identified | Legislative database / human confirmation | PRE_EVT → INTRO_EVT |
| Committee Referral | Congressional schedule / human confirmation | INTRO_EVT → COMM_EVT |
| Floor Scheduling | Congressional schedule / human confirmation | COMM_EVT → FLOOR_EVT |
| Vote Scheduling | Congressional schedule / human confirmation | FLOOR_EVT → FINAL_EVT |
| Law Enactment | Legislative database / human confirmation | FINAL_EVT → IMPL_EVT |

### 8.2 External Event Validation

**Validation Rules:**
1. External events must be confirmed by authoritative source (legislative database) OR human confirmation
2. Human confirmation must include:
   - Confirmation timestamp
   - Confirming party identifier
   - Source reference
3. External events cannot be auto-generated by agents
4. Event confirmation must be logged in state history

---

## 9. Artifact Dependency Graph

### 9.1 Artifact Prerequisites

| Artifact | Depends On | Blocks State Advancement |
|----------|-----------|-------------------------|
| Concept Memo | Signal Scan (optional), Stakeholder Map (optional) | PRE_EVT → INTRO_EVT |
| Policy Framing | Concept Memo (approved) | INTRO_EVT → COMM_EVT |
| Policy Whitepaper | Concept Memo (approved) | INTRO_EVT → COMM_EVT |
| Legislative Language | Policy Framing (approved), Policy Whitepaper (approved) | COMM_EVT → FLOOR_EVT |
| Amendment Strategy | Legislative Language (approved) | COMM_EVT → FLOOR_EVT |
| Floor Messaging | Legislative Language (approved) | FLOOR_EVT → FINAL_EVT |
| Media Narrative | Floor Messaging (approved) | FLOOR_EVT → FINAL_EVT |
| Final Narrative | Floor Messaging (approved), Media Narrative (approved) | FINAL_EVT → IMPL_EVT |
| Outcome Report | All prior artifacts (completed) | IMPL_EVT (post-state) |

---

## 10. System Invariants Summary

### 10.1 State Machine Invariants

1. **Unidirectional Flow**: Legislative states advance only forward, never backward
2. **Sequential Progression**: States must be traversed in order (no skipping)
3. **Terminal Immutability**: IMPL_EVT is terminal; no exit transitions
4. **State Authority**: Only external events or human confirmation advance state
5. **Agent Scoping**: Agents are state-bounded and ephemeral

### 10.2 Artifact Invariants

1. **Required Artifacts**: Each state has minimum required artifacts before advancement
2. **Approval Blocking**: Artifacts requiring human review block state advancement until approved
3. **Dependency Chain**: Artifacts have explicit dependencies that must be satisfied
4. **Audit Trail**: All artifact creation, approval, and rejection is logged

### 10.3 Agent Invariants

1. **Type Eligibility**: Agent types are only spawnable in eligible states
2. **Scope Boundaries**: Every agent has explicit scope and termination condition
3. **Non-Persistence**: Agents never persist beyond their scope or state eligibility
4. **Review Gating**: Drafting and Execution agents cannot self-release outputs

### 10.4 Orchestrator Invariants

1. **State-Driven Execution**: Orchestrator behavior is determined by current legislative state
2. **Agent Governance**: Orchestrator spawns, monitors, and terminates all agents
3. **Review Gate Enforcement**: Orchestrator blocks state advancement until gates are satisfied
4. **Error Recovery**: Orchestrator handles agent failures without advancing state incorrectly

---

**Document Authority:** This document defines the authoritative invariants for the Agent Orchestrator system. All implementations must conform to these rules. Violations constitute system errors and must be logged and audited.
