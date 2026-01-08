# Wi-Charge OEM Risk Proposal Generator - System Architecture

## Overview

This system processes OEM (Original Equipment Manufacturer) PDFs to generate risk proposals for Wi-Charge wireless power integration. The system follows a multi-stage pipeline with AI personas, human review gates, and deterministic execution zones.

## System Flow

### 1. 🧲 INPUT INTAKE — Messy, Untrusted
- **Input**: Raw OEM & Sales PDFs
- **Process**: Orchestrate OEM PDF Intake
- **Output**: `raw_docs.zip` (Ingested OEM PDFs)

### 2. 🔍 INTELLIGENCE & EXTRACTION — Structure Facts
- **Process**: Learn OEM Engineering Context
- **Output**: `oem_specs.json` (Engineering Constraints)
- **Artifact**: OEM Engineering Profile

- **Process**: Learn Wi-Charge Integration Surface
- **Output**: `wpc_integration.json` (Wi-Charge Power Needs Mapping)
- **Artifact**: Wi-Charge Integration Map

### 3. 🧠 VIBE CODING ZONE — Heuristics & Strategy
- **Process**: Infer Value Proposition
- **Output**: `value_map.md` (Value Proposition Map)
- **Artifact**: Value Proposition Map

- **Process**: Reason About Insurable Risk
- **Output**: `risk_hypotheses.json` (Insurable Risk Hypotheses)
- **Artifact**: Insurable Risk Hypotheses

### 4. 🛠️ EXECUTION ZONE — Deterministic Builds
- **Process**: Retrieve Insurance Reference Data
- **Output**: `insurance_refs.csv` (Battery Insurance Data)
- **Artifact**: Insurance Reference Dataset

- **Process**: Train Risk Correlation Model
- **Output**: `risk_model.pkl` (Trained Risk Model)
- **Artifact**: Trained Risk Model

### 5. 🧾 REVIEW & SIGN-OFF — Human Authority
- **Review Gate**: Human Review Required - Risk Validity
- **Output**: `Copy-Safe Risk Mapping Report.pdf`
- **Artifact**: OEM Integration & Insurance Brief

### 6. 🛠️ EXECUTION ZONE — Python Automation & Logging
- **Process**: Log Artifacts with Python
- **Output**: `pipeline_log.jsonl` (Execution & Data Lineage Log)

- **Process**: Snapshot Model Outputs
- **Output**: `model_samples.csv` (Sampled Model Outputs)

### 7. 🧾 REVIEW & SIGN-OFF — Human Reference Validation
- **Review Gate**: Human Review Required - Reference Accuracy

### 8. 🧾 REVIEW & SIGN-OFF — Output Structuring
- **Review Gate**: Human Consultation - Output Format & Framing
- **Output**: `Copy-Safe Logged Risk Report.pdf`
- **Artifact**: Human-Structured OEM Risk & Integration Brief

### 9. 🧠 VIBE CODING ZONE — AI Personas from Field Experts
- **Process**: Simulate Insurance Underwriter Persona
- **Process**: Simulate Built-Environment Risk Engineer Persona
- **Process**: Simulate Wireless Power Safety Expert Persona
- **Output**: `persona_insights.md` (AI Persona Insights)
- **Artifact**: AI Persona Insights

### 10. 🧾 REVIEW & SIGN-OFF — Persona-Informed Judgment
- **Review Gate**: Human Review Required - Persona Alignment

### 11. 🧊 TRUSTED & CONSUMER OUTPUTS — Finalized
- Final outputs ready for consumption

## Key Components

### AI Personas
1. **Insurance Underwriter Persona** - Evaluates insurability and risk assessment
2. **Built-Environment Risk Engineer Persona** - Assesses physical installation risks
3. **Wireless Power Safety Expert Persona** - Evaluates technical safety and compliance

### Review Gates
1. Risk Validity Review
2. Reference Accuracy Review
3. Output Format & Framing Consultation
4. Persona Alignment Review

### Output Artifacts
- `oem_specs.json` - Engineering constraints
- `wpc_integration.json` - Wi-Charge integration mapping
- `value_map.md` - Value proposition
- `risk_hypotheses.json` - Risk hypotheses
- `risk_model.pkl` - Trained risk model
- `Copy-Safe Risk Mapping Report.pdf` - Initial risk report
- `Copy-Safe Logged Risk Report.pdf` - Final risk report
- `pipeline_log.jsonl` - Execution log
- `model_samples.csv` - Model output samples
- `persona_insights.md` - AI persona insights

## System Principles

1. **Trusted Outputs Only** - All outputs go through human review gates
2. **Persona-Informed** - AI personas simulate expert judgment
3. **Deterministic Execution** - Python automation ensures reproducibility
4. **Complete Lineage** - All artifacts are logged with full provenance
5. **Copy-Safe Reports** - Final outputs are sanitized for external use
