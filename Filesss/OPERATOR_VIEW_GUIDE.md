# Operator View Guide

**Purpose:** Guide for using state-specific operator views and understanding when to reference the master diagram.

**Version:** 1.0.0  
**Last Updated:** 2026-01-20

---

## 📍 Overview

This guide explains how to use the state-specific operator views (`*_operator_view.mmd` files) and when to reference the master diagram (`agent orchestrator 1.6.mmd`).

The operator views are **specialized, focused diagrams** that show only the actions, processes, and agents relevant to a specific legislative state. They are designed to reduce cognitive load and provide clear, actionable views for operators.

---

## 🎯 When to Use Operator Views

### Use Operator Views When:

1. **Working in a specific state** — You're actively operating in PRE_EVT, COMM_EVT, FLOOR_EVT, FINAL_EVT, or IMPL_EVT
2. **Understanding state-specific workflows** — You need to see what actions and processes are available in the current state
3. **Planning state-specific operations** — You're planning agent spawns, reviewing gates, or execution activities for a specific state
4. **Training or onboarding** — You're learning how a specific state works or teaching others

### Use Master Diagram When:

1. **Understanding system architecture** — You need to see the complete system structure
2. **Understanding state transitions** — You need to see how states connect and what triggers transitions
3. **System design or planning** — You're designing new features, agents, or processes
4. **Cross-state dependencies** — You need to understand how processes in one state affect another
5. **Complete context** — You need to see all components, services, and relationships

---

## 📊 Available Operator Views

### PRE_EVT Operator View

**File:** `.userInput/agent orchestrator 1.6_PRE_EVT_operator_view.mmd`

**Shows:**
- Policy opportunity detection
- Signal scanning and stakeholder mapping
- Concept memo generation
- HR_PRE review gate
- Intelligence and drafting agents for PRE_EVT
- External reality triggers (elections, courts, agencies, markets)
- Professional context and guidance

**Key Focus:** Initial opportunity identification and concept development

**Next State:** INTRO_EVT (Bill Vehicle Identified)

---

### COMM_EVT Operator View

**File:** `.userInput/agent orchestrator 1.6_COMM_EVT_operator_view.mmd`

**Shows:**
- Committee referral and agenda analysis
- Committee briefing packets and legislative language
- Amendment strategy
- HR_LANG review gate
- Drafting and execution agents for COMM_EVT
- Execution loop (strategy, tactics, monitoring)
- Campaign operations (committee outreach, coalition expansion)
- Memory and learning systems

**Key Focus:** Committee work, legislative language, and tactical execution

**Previous State:** PRE_EVT  
**Next State:** FLOOR_EVT (Floor Scheduled)

---

### FLOOR_EVT Operator View

**File:** `.userInput/agent orchestrator 1.6_FLOOR_EVT_operator_view.mmd`

**Shows:**
- Floor scheduling and messaging
- Vote whip strategy and timing
- Press and media narrative
- HR_MSG review gate
- Drafting and execution agents for FLOOR_EVT
- Execution loop with monitoring and alerts
- Campaign operations (narrative reframing, opposition neutralization)
- Opportunity windows (messaging, member, amendment, media)
- Marketing intelligence and message testing
- Momentum signals

**Key Focus:** Floor activity, messaging, and real-time monitoring

**Previous State:** COMM_EVT  
**Next State:** FINAL_EVT (Vote Imminent)

---

### FINAL_EVT Operator View

**File:** `.userInput/agent orchestrator 1.6_FINAL_EVT_operator_view.mmd`

**Shows:**
- Vote imminent state
- Coalition activation
- Final constituent narrative
- HR_RELEASE review gate
- Execution agents for FINAL_EVT
- Execution loop (final push)
- Campaign operations (coalition expansion, narrative push)
- Outbound influence actions (partner activation, media seeding)
- Memory and learning systems
- Learning agents (tactic performance, narrative effectiveness, outcome attribution)

**Key Focus:** Final vote preparation and coalition mobilization

**Previous State:** FLOOR_EVT  
**Next State:** IMPL_EVT (Law Enacted)

---

### IMPL_EVT Operator View

**File:** `.userInput/agent orchestrator 1.6_IMPL_EVT_operator_view.mmd`

**Shows:**
- Law enacted state
- Implementation guidance
- Oversight and compliance preparation
- Outcome and impact reporting
- Execution loop (post-enactment monitoring)
- Memory and learning systems (primary focus)
- Learning agents (causal attribution, strategy reweighting, performance learning)
- Post-enactment review and audit

**Key Focus:** Post-enactment monitoring, learning, and outcome attribution

**Previous State:** FINAL_EVT  
**Next State:** Terminal (no next state)

---

## 🎨 Visual Semantics

All operator views use consistent visual semantics defined in the master diagram:

### HUMAN_ACTION (Thick Black Border)
- **Human decisions required**
- Review gates (HR_PRE, HR_LANG, HR_MSG, HR_RELEASE)
- Escalation points
- Final approval decisions

**Examples:**
- HR_PRE, HR_LANG, HR_MSG, HR_RELEASE
- ESC_RISK, ESC_OVERRIDE
- FB_HUMAN, FINAL_EVT

---

### SYSTEM_FLOW (Gray Box)
- **System running automatically**
- State transitions (PRE_EVT, INTRO_EVT, COMM_EVT, etc.)
- AI services (AI_INGEST, AI_RETRIEVE, AI_GENERATE, etc.)
- Execution loop (EXEC_STRATEGY, EXEC_TACTICS, EXEC_RUN, etc.)

**Examples:**
- PRE_EVT, COMM_EVT, FLOOR_EVT, FINAL_EVT, IMPL_EVT
- AI_CORE, AI_INGEST, AI_GENERATE, AI_SCORE
- EXEC_STRATEGY, EXEC_TACTICS, EXEC_RUN, EXEC_MONITOR

---

### CONTEXT_REF (Dashed Border)
- **Reference / context information**
- Memory and learning systems
- Orientation and guidance
- Professional context
- External reality

**Examples:**
- MEMORY, MEM_EVIDENCE, MEM_TACTICS, MEM_NARRATIVE, MEM_OUTCOMES
- ORIENTATION, CONTINUITY, EXECUTION_SCOPE
- REALITY, MARKETING, GOVERNANCE

---

### Thick Arrows (3px stroke-width)
- **Blocking paths and state transitions**
- Critical flow paths that require attention
- State-to-state transitions
- Human review gate blocking connections (--o)

**Examples:**
- PRE_EVT --> INTRO_EVT
- COMM_EVT --> FLOOR_EVT
- HR_PRE --o INTRO_EVT (blocking connection)

---

## 📖 Reading Operator Views

### 1. Identify Current State

Look for the state node in the center (PRE_EVT, COMM_EVT, etc.). This is your current operational state.

### 2. Identify Human Actions Required

Look for nodes with **HUMAN_ACTION** styling (thick black borders):
- These are the human decisions you need to make
- Review gates require your approval before state advancement
- Escalation points may require strategic intervention

### 3. Understand System Flow

Look for nodes with **SYSTEM_FLOW** styling (gray boxes):
- These are processes running automatically
- State transitions show where you're going next
- AI services and execution loops show what's happening now

### 4. Review Context

Look for nodes with **CONTEXT_REF** styling (dashed borders):
- These provide background information
- Memory systems show historical data
- Learning systems show what's being learned

### 5. Follow Thick Arrows

Follow thick arrows (3px) to understand:
- Critical flow paths
- State transitions
- Blocking paths (what's waiting on you)

---

## 🔄 State Transitions

Operator views show state transitions but focus on the current state. To understand full transition logic:

1. **Reference the master diagram** for complete state machine
2. **Check transition requirements** (artifacts, review gates, external confirmations)
3. **See PREVIOUS STATE and NEXT STATE** nodes in operator views for context

---

## 🧩 Agent Spawn Rules

Each operator view shows which agents can be spawned in that state:

- **PRE_EVT:** Intelligence + Drafting agents
- **COMM_EVT:** Drafting + Execution agents
- **FLOOR_EVT:** Execution + Monitoring agents
- **FINAL_EVT:** Execution + Learning agents
- **IMPL_EVT:** Learning agents only

For complete agent spawn rules, see the master diagram.

---

## 📚 Master Diagram Reference

**File:** `.userInput/agent orchestrator 1.6.mmd`

**When to reference:**
- Understanding complete system architecture
- Seeing all states and transitions
- Understanding cross-state dependencies
- System design and planning
- Complete agent orchestration model
- All services, systems, and relationships

**Master diagram shows:**
- Complete legislative spine (all states)
- All AI services and execution loops
- All human review gates
- All agent types and spawn rules
- All campaign operations
- All memory and learning systems
- Complete orchestration model
- Cursor agent interpretation layer

---

## 🚀 Quick Start

1. **Identify your current state** (PRE_EVT, COMM_EVT, etc.)
2. **Open the corresponding operator view** (`*_STATE_operator_view.mmd`)
3. **Look for HUMAN_ACTION nodes** (what you need to do)
4. **Follow SYSTEM_FLOW nodes** (what's running automatically)
5. **Review CONTEXT_REF nodes** (background information)
6. **Follow thick arrows** (critical paths and transitions)
7. **Reference master diagram** when you need complete context

---

## ⚠️ Important Notes

1. **Operator views are focused** — They show only state-specific information
2. **Master diagram is complete** — It shows everything in one view
3. **Styling is consistent** — All views use the same visual semantics
4. **State transitions are shown** — Previous and next states are indicated
5. **Agent spawn rules are implicit** — Only relevant agents are shown

---

## 📝 Maintenance

When updating diagrams:

1. **Update master diagram first** — It's the source of truth
2. **Update operator views** — Align with master diagram changes
3. **Maintain visual semantics** — Keep styling classes consistent
4. **Update this guide** — Document new states or changes

---

## 🔗 Related Documents

- **Master Diagram Reference:** `MASTER_DIAGRAM_REFERENCE.md`
- **Authoritative Invariants:** `AUTHORITATIVE_INVARIANTS.md`
- **Component Mapping:** `COMPONENT_MAPPING.md`
- **Diagram Output Contract:** `diagrams/DIAGRAM_OUTPUT_CONTRACT.md`

---

**Last Updated:** 2026-01-20  
**Version:** 1.0.0
