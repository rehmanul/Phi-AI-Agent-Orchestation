# Master System Architecture Diagram

**Authoritative Source:** `.userInput/agent orchestrator 1.6.mmd`

This Mermaid diagram (939 lines) is the **spine of the entire project** and shows everything.

---

## 📍 Location

```
C:\Users\phi3t\12.20 dash\1.5.2026\.userInput\agent orchestrator 1.6.mmd
```

**Relative Path:** `.userInput/agent orchestrator 1.6.mmd`

---

## 🎯 What It Shows

### Core Components

1. **Legislative Process Spine** (Authoritative Timeline)
   - PRE_EVT → INTRO_EVT → COMM_EVT → FLOOR_EVT → FINAL_EVT → IMPL_EVT
   - All artifacts, human actions, and decision points

2. **AI Service Execution Layer**
   - Multi-source ingestion
   - Contextual retrieval
   - Feature extraction
   - Draft & strategy generation
   - Impact & risk scoring

3. **Human Review Gates**
   - HR_PRE, HR_LANG, HR_MSG, HR_RELEASE
   - Cost, effort, and risk signaling

4. **Memory & Learning Systems**
   - Evidence store
   - Tactic performance history
   - Narrative effectiveness log
   - Legislative outcomes
   - Causal attribution engine

5. **Execution Loop**
   - Strategy decomposition
   - Tactical planning
   - Tactic execution engine
   - Live monitoring
   - Tactical retuning

6. **Agent Orchestration Model**
   - Orchestrator logic (state cursor, permissions, spawn/retire rules)
   - Agent types (Intelligence, Drafting, Execution, Learning)
   - Agent lifecycle
   - Hard safety constraints

7. **Campaign Operations**
   - Committee outreach
   - Narrative reframing
   - Coalition expansion
   - Opposition neutralization

8. **Business Development**
   - Industry demand signals
   - Strategic partnerships
   - Value proposition mapping

9. **Advocacy & Pressure**
   - Constituent base activation
   - Staff/member-level persuasion
   - Opposition pressure & counter-pressure

10. **Software Systems**
    - Background jobs
    - Event bus
    - External APIs
    - Observability

11. **Professional Service Field**
    - Regulatory affairs
    - Legislative policy
    - Compliance & ethics
    - Industry expertise
    - Communications & media

12. **Cursor Agent Interpretation Layer**
    - Diagram reading & topology parsing
    - Legislative spine binding
    - Agent role identification
    - Work planning
    - Template resolution

---

## 🔗 Relationship to Other Diagrams

All other system diagrams should reference or derive from this master diagram:

- `monitoring/DASHBOARD_SYSTEM_CONTEXT.mmd` - Dashboard-specific view
- `execution/PHASE3_SYSTEM_CONTEXT.mmd` - Execution layer focus
- `artifacts/policy/diagrams/system_context.mmd` - Policy artifacts integration
- All other diagrams are **subsets** or **specialized views** of this master

---

## 📋 Usage

### For Codex Review
Reference this diagram when:
- Understanding system architecture
- Planning new features
- Reviewing integration work
- Understanding agent orchestration
- Clarifying state machine logic

### For Development
- **Source of Truth:** All system design should align with this diagram
- **State Machine:** Legislative spine defines all state transitions
- **Agent Rules:** All agent behavior should follow constraints shown here
- **Integration Points:** Shows where new components should connect

---

## ⚠️ Important Notes

1. **This diagram is authoritative** - it shows the complete system
2. **Legislative Spine is the backbone** - all state flows through it
3. **AI_CORE is the orchestrator** - not a worker, but the control plane
4. **All agents are spawned** - ephemeral, scoped, and retired
5. **Human gates are non-negotiable** - shown as decision diamonds
6. **Cursor agents interpret this** - they read and bind to the spine

---

## 🔄 Updates

When the master diagram changes:
1. Update this reference document
2. Review all derived diagrams for alignment
3. Update agent rules if state machine changes
4. Update documentation that references the system

---

**Last Verified:** 2026-01-07  
**Diagram Version:** 1.6  
**Status:** ✅ Active & Authoritative
