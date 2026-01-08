# Human Decision Checklist
## ML + Legislative + Actuarial Architecture

**Status:** ⏸️ NON-AUTHORITATIVE — FOR HUMAN REVIEW  
**Generated:** 2026-01-20  
**Purpose:** Define what humans must approve at each stage

---

## 🎯 OVERVIEW

This checklist defines **explicit human decision points** across all 8 ML insertion layers and 4 human review gates. Each decision point specifies:

- **What** ML attempted to do
- **What** was blocked by guardrails
- **What** evidence is surfaced for human review
- **What** approval criteria must be met

**NO ML PATH MAY BYPASS HUMAN APPROVAL.**

---

## 🔴 CRITICAL DECISION GATES

### HR_PRE: Pre-Event Approval Gate

**Location:** Between `PRE_CONCEPT` and `INTRO_EVT`

**ML Inputs:**
- Layer 1 ML Services generate concept memos with:
  - NLP topic modeling from PDFs, meeting notes, emails
  - Issue clustering (nonprofits, OEMs, insurers)
  - Signal detection (pain points, regulatory demand)

**What Gets Blocked:**
- ✅ Concept memo cannot advance to bill vehicle identification (`INTRO_EVT`)
- ✅ Legislative state cannot progress without HR_PRE approval

**Evidence Surfaces for Human Review:**
- Concept memo artifact with `[SPECULATIVE]` tag
- Confidence scores from ML models
- Risk taxonomy suggestions
- False-positive flags
- Hallucination warnings

**Human Must Approve:**
- [ ] Policy direction alignment
- [ ] Signal interpretation accuracy
- [ ] Risk taxonomy completeness
- [ ] Stakeholder mapping validity
- [ ] Concept memo quality sufficient to proceed

**Approval Criteria:**
- Concept memo demonstrates clear policy opportunity
- Risk assessment is comprehensive
- Stakeholder analysis is complete
- No critical false positives detected
- Hallucination warnings addressed

**If Rejected:**
- Return to PRE_SIGNAL_SCAN for additional intelligence gathering
- ML may regenerate concept memo with corrections

---

### HR_LANG: Legislative Language Approval Gate

**Location:** Between `COMM_LANG` and `FLOOR_EVT`

**ML Inputs:**
- Layer 3 Risk Scan ML may influence language via:
  - Text-to-risk mapping (bill language → insurance clauses)
  - Standards reference detection (NFPA, UL, FM)
- Layer 4 Modeling ML may suggest:
  - Risk-aligned language modifications

**What Gets Blocked:**
- ✅ Draft legislative language cannot advance to floor scheduling
- ✅ Language cannot be finalized without HR_LANG approval

**Evidence Surfaces for Human Review:**
- Draft language with ML-suggested modifications
- Risk analysis of language impact
- Standards compliance check
- Control gap analysis
- Model confidence bounds

**Human Must Approve:**
- [ ] Legislative language is legally sound
- [ ] Language aligns with policy intent
- [ ] Risk implications are acceptable
- [ ] Standards references are correct
- [ ] No unintended consequences

**Approval Criteria:**
- Language is statutorily defensible
- Risk analysis confirms language safety
- Standards compliance verified
- No control gaps introduced
- Language supports actuarial modeling

**If Rejected:**
- Return to COMM_LANG for revision
- ML may suggest alternative language with risk analysis

---

### HR_MSG: Messaging & Narrative Approval Gate

**Location:** Between `FLOOR_MEDIA` and `FINAL_EVT`

**ML Inputs:**
- Layer 1 ML Services may generate:
  - Topic modeling for messaging alignment
  - Signal detection for narrative opportunities
- Layer 2 ML Services may suggest:
  - Legislator-specific messaging based on affinity scoring

**What Gets Blocked:**
- ✅ Floor messaging cannot advance to final vote stage
- ✅ Media narrative cannot be released without HR_MSG approval

**Evidence Surfaces for Human Review:**
- Floor messaging document
- Media narrative with ML-generated suggestions
- Reputational risk scoring
- Legislator affinity analysis
- Topic alignment scores

**Human Must Approve:**
- [ ] Messaging is accurate and defensible
- [ ] Narrative aligns with coalition positions
- [ ] Reputational risks are acceptable
- [ ] Legislator targeting is appropriate
- [ ] Media strategy is sound

**Approval Criteria:**
- Messaging is factually accurate
- Narrative supports policy goals
- Reputational risk is manageable
- Legislator targeting is ethical
- Media strategy is executable

**If Rejected:**
- Return to FLOOR_MSG for revision
- ML may regenerate messaging with different framing

---

### HR_RELEASE: Public Release Authorization Gate

**Location:** Between `FINAL_NARR` and `IMPL_EVT`

**ML Inputs:**
- Minimal ML inputs at this stage (correctly positioned)
- Layer 7 Monitoring ML may detect:
  - Anomalies that affect release timing

**What Gets Blocked:**
- ✅ Final narrative cannot trigger implementation
- ✅ Public release cannot occur without HR_RELEASE approval

**Evidence Surfaces for Human Review:**
- Final constituent narrative
- Implementation readiness assessment
- Any monitoring alerts from Layer 7

**Human Must Approve:**
- [ ] Narrative is ready for public release
- [ ] Implementation guidance is complete
- [ ] No blocking issues detected
- [ ] Timing is appropriate

**Approval Criteria:**
- Narrative is complete and accurate
- Implementation guidance is actionable
- No critical issues outstanding
- Release timing is optimal

**If Rejected:**
- Return to FINAL_NARR for revision
- Delay implementation until resolved

---

## 📊 ML LAYER-SPECIFIC DECISION POINTS

### Layer 1: PRE-LEGISLATION ML Services

**Decision Point:** `RISK1_VALIDATE` → Human Validation Gate

**What ML Attempts:**
- Generates concept memo from signal scan
- Clusters issues by stakeholder type
- Detects pain points and regulatory demand signals

**What Gets Blocked:**
- All outputs tagged `[SPECULATIVE]` until HR_PRE approval
- False positives suppressed but flagged for review

**Evidence Surfaces:**
- Concept memo with confidence scores
- Issue clustering results
- Signal detection report
- False-positive flags

**Human Must Review:**
- [ ] Signal interpretation accuracy
- [ ] Issue clustering validity
- [ ] Pain point identification
- [ ] Regulatory demand assessment

---

### Layer 2: INTRODUCTION ML Services

**Decision Point:** `RISK2_VETO` → Human Veto Gate

**What ML Attempts:**
- Recommends sponsor based on affinity scoring
- Analyzes legislative survivability
- Assesses reputational risk

**What Gets Blocked:**
- ✅ **NO AUTONOMOUS SPONSOR SELECTION** — Human veto gate prevents automation
- ML recommendation is advisory only

**Evidence Surfaces:**
- Sponsor recommendation with affinity scores
- Legislative survivability probability
- Reputational risk assessment
- Sponsor mismatch warnings

**Human Must Review:**
- [ ] Sponsor recommendation validity
- [ ] Affinity scoring accuracy
- [ ] Survivability model assumptions
- [ ] Reputational risk acceptability

---

### Layer 3: RISK SCAN ML Enhancement

**Decision Point:** `RISK3_CONFIDENCE` → Model Confidence Bounds

**What ML Attempts:**
- Classifies tail risk vs manageable risk
- Maps bill language to insurance clauses
- Detects standards references

**What Gets Blocked:**
- Low-confidence outputs forced to human review
- Standards gaps flagged for engineering review

**Evidence Surfaces:**
- Risk classification results
- Text-to-risk mapping
- Standards detection report
- Confidence scores

**Human Must Review:**
- [ ] Risk classification accuracy
- [ ] Text-to-risk mapping validity
- [ ] Standards coverage completeness
- [ ] Control gap analysis

---

### Layer 4: MODELING ML Enhancement

**Decision Point:** `RISK4_ASSUMPTIONS` → Human-Approved Assumptions Gate

**What ML Attempts:**
- Generates probabilistic loss models
- Performs sensitivity analysis
- Models tail-risk compression

**What Gets Blocked:**
- ✅ **NO BLACK-BOX PARAMETER CHANGES** — All assumptions require human approval
- Model changes blocked until approved

**Evidence Surfaces:**
- Probabilistic model outputs
- Sensitivity analysis results
- Counterfactual simulations
- Tail-risk compression curves
- Assumption documentation

**Human Must Review:**
- [ ] Model assumptions are valid
- [ ] Probabilistic ranges are defensible
- [ ] Sensitivity analysis is complete
- [ ] Tail-risk modeling is accurate

---

### Layer 5: UNDERWRITING ML Services

**Decision Point:** `RISK5_DOCTRINE` → Eligibility ≠ Price Doctrine Gate

**What ML Attempts:**
- Classifies eligibility (Pass / Conditional / Fail)
- Scores control effectiveness
- Models portfolio impact

**What Gets Blocked:**
- ✅ **ELIGIBILITY ≠ PRICING** — ML influences eligibility only; humans set pricing
- Underwriter override required and logged

**Evidence Surfaces:**
- Eligibility classification
- Control effectiveness scores
- Portfolio impact analysis
- Regulatory defensibility report

**Human Must Review:**
- [ ] Eligibility classification accuracy
- [ ] Control effectiveness assessment
- [ ] Portfolio impact is acceptable
- [ ] Pricing decision (human-only)

---

### Layer 6: REINSURANCE ML Services

**Decision Point:** `RISK6_NO_AUTO` → No Automated Treaty Placement Gate

**What ML Attempts:**
- Aggregates portfolio-level risks
- Models tail dependencies
- Estimates capital relief
- Suggests attachment point optimization

**What Gets Blocked:**
- ✅ **NO AUTOMATED TREATY PLACEMENT** — Human reinsurer review required

**Evidence Surfaces:**
- Portfolio aggregation results
- Tail dependency modeling
- Capital relief estimates
- Attachment point recommendations
- Reinsurer comfort scores

**Human Must Review:**
- [ ] Portfolio aggregation accuracy
- [ ] Tail dependency modeling validity
- [ ] Capital relief estimates reasonableness
- [ ] Attachment point optimization
- [ ] Treaty placement decision (human-only)

---

### Layer 7: IMPLEMENTATION & MONITORING ML

**Decision Point:** `RISK7_ROLLBACK` → Model Rollback Capability

**What ML Attempts:**
- Detects anomalies (sensor dropouts, environmental drift)
- Monitors model assumption drift
- Feeds claims data back to models

**What Gets Blocked:**
- Anomaly detection triggers alerts (human review)
- Model drift triggers recalibration review
- Rollback capability exists but requires human authorization

**Evidence Surfaces:**
- Anomaly detection alerts
- Drift monitoring reports
- Claims vs model prediction comparisons
- Rollback recommendations

**Human Must Review:**
- [ ] Anomaly validity (false alarm vs real issue)
- [ ] Drift severity assessment
- [ ] Recalibration necessity
- [ ] Rollback authorization

---

### Layer 8: CROSS-CUTTING GUARDRAILS

**Decision Point:** All ML outputs route through `GUARD_APPROVAL`

**What ML Attempts:**
- All layers generate outputs that must pass guardrails

**What Gets Blocked:**
- ✅ All ML outputs tagged `[NON-AUTHORITATIVE]` until human approval
- Artifact versioning prevents unauthorized changes
- Phase gates enforce sequential progression
- Role separation prevents unauthorized actions

**Evidence Surfaces:**
- Versioned artifacts
- Role-based audit trail
- Phase gate status
- READ-ONLY policy markers

**Human Must Review:**
- [ ] Artifact versions are correct
- [ ] Role assignments are appropriate
- [ ] Phase progression is valid
- [ ] Policy context markers are accurate

---

## ✅ DECISION FLOW SUMMARY

```
ML Output → [SPECULATIVE] Tag → Guardrail Validation → Human Gate → [ACTIONABLE] → Progression
```

**Key Rules:**
1. **NO ML OUTPUT IS ACTIONABLE** until human approval
2. **ALL ML OUTPUTS** must pass through guardrails
3. **ALL HUMAN GATES** are blocking (no bypass)
4. **ALL DECISIONS** are logged in audit trail

---

## 🚨 ESCALATION CRITERIA

**Escalate to Human Immediately If:**
- ML confidence score < 70%
- False-positive suppression fails
- Model assumptions diverge >20% from actual outcomes
- Anomaly detection triggers high-severity alert
- Any ML output bypasses a human gate (CRITICAL FAILURE)

**Escalate for Review (Non-Blocking):**
- ML confidence score 70-85% (may proceed with caution)
- Low-severity anomaly detection
- Routine model recalibration requests
- Version conflicts in artifacts

---

## 📝 AUDIT REQUIREMENTS

**Every Human Decision Must Log:**
- Decision timestamp (ISO-8601 UTC)
- Decision maker identity
- ML output reviewed
- Approval or rejection
- Rationale for decision
- Any modifications made to ML output

**Audit Trail Format:**
```json
{
  "timestamp": "2026-01-20T12:00:00Z",
  "decision_gate": "HR_PRE",
  "decision_maker": "human:reviewer_id",
  "ml_output_id": "PRE_CONCEPT_v1.0",
  "decision": "approved" | "rejected" | "modified",
  "rationale": "Human-readable explanation",
  "modifications": ["List of changes made"],
  "confidence_override": "HIGH" | "MEDIUM" | "LOW"
}
```

---

**NON-AUTHORITATIVE — FOR HUMAN REVIEW**  
**This checklist must be reviewed and approved before deployment**
