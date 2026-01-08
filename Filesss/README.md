# Agentic Coding Development Workflow

Implementation of the agentic coding development workflow from Diagram 5.

## Workflow Structure

1. **Knowledge Spine** - Gathers context from multiple sources
2. **Agentic Reasoning Core** - 7-step reasoning process:
   - Pattern Recall
   - Differential Expansion
   - Evidence Mapping
   - Failure Mode Enumeration
   - Boundary/Stress Modeling
   - Optionality Analysis
   - Confidence Banding
3. **Control Gates** - Evaluates if workflow can proceed:
   - Evidence Sufficient?
   - Harm Asymmetry?
   - Differential Preserved?
   - Human Review Completed?
4. **Traceable Outputs** - Generates reviewable artifacts:
   - Draft Narrative
   - Differential Table
   - Evidence Gaps
   - Confidence Bands
   - Decision Log

## Running the Workflow

```bash
python run_workflow.py
```

## Output Structure

Outputs are saved to `output/workflow_YYYYMMDD_HHMMSS/`:

- `draft_narrative.md` - Implementation plan narrative
- `differential_table.json` - Alternative approaches comparison
- `evidence_gaps.json` - Missing information or clarifications needed
- `confidence_bands.json` - Confidence levels for different aspects
- `decision_log.json` - Complete workflow decision history
- `workflow_summary.json` - Complete workflow state

## Example

The workflow analyzes a coding task and produces structured outputs that can be reviewed before implementation.
