# Risk Management Workflow System

A comprehensive 7-phase risk management system for evaluating opportunities, assets, and policies. Designed for risk managers (FRM/CFA) with structured intake, AI-powered risk scanning, non-Gaussian modeling, ruin gate checks, and human approval workflows.

## Architecture

The system follows a 7-phase workflow:

1. **Phase 1 - Intake & Framing**: Document upload, assumption extraction, failure-first thinking
2. **Phase 2 - Agentic Risk Scan**: Tail risk, incentive, and regulatory analysis
3. **Phase 3 - Modeling**: Non-Gaussian modeling, scenario trees, stress testing
4. **Phase 4 - Memory**: Historical data, near misses, assumption logs
5. **Phase 5 - Ruin Gates**: Kill switches (ruin check, asymmetry check, redundancy check)
6. **Phase 6 - Human Judgment**: Professional review, context check, approval workflow
7. **Phase 7 - Execution & Learning**: Real-world tracking, monitoring, model updates

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
cd risk-management-system
pip install -r requirements.txt
```

### Running the API

```bash
python -m api.main
```

API will be available at `http://localhost:8002`

## Directory Structure

```
risk-management-system/
├── api/                    # FastAPI application
│   ├── routes/            # API endpoints
│   └── main.py            # Application entry point
├── agents/                # Agent implementations
│   ├── intake/           # Phase 1 agents
│   ├── knowledge/        # Academic knowledge base
│   ├── risk_scan/        # Phase 2 agents
│   ├── modeling/         # Phase 3 agents
│   ├── memory/           # Phase 4 agents
│   ├── ruin_gates/       # Phase 5 agents
│   ├── judgment/         # Phase 6 agents
│   ├── execution/        # Phase 7 agents
│   ├── orchestrator/     # Workflow orchestration
│   └── utils/            # Shared utilities
├── schemas/              # Data schemas
├── config/               # Configuration files
├── data/                 # Data storage
│   ├── raw/              # Raw uploaded documents
│   ├── processed/        # Processed artifacts
│   ├── memory/           # Historical data and logs
│   ├── knowledge/        # Academic corpus
│   ├── reviews/          # Review artifacts
│   ├── execution/        # Execution tracking
│   └── learning/         # Model updates
└── tests/                # Test suite
```

## Workflow

1. **Upload Documents**: User provides proposal/asset/policy documents
2. **Intake Processing**: Extract assumptions, identify hidden assumptions, synthesize failure-first thinking
3. **Risk Scanning**: AI agents scan for tail risks, incentive misalignments, regulatory exposures
4. **Modeling**: Calculate bounds, build scenarios, stress test beyond history
5. **Ruin Gates**: Check for ruin possibility, downside capping, redundancy
6. **Human Review**: Professional validation, context check, approval decision
7. **Execution**: Track real-world outcomes, monitor continuously, update models

## Data Governance

- All source files are hashed and registered
- Lineage tracking logs all transformations
- Schemas are frozen in `schemas/`
- All outputs are reproducible from lineage logs
- Human review gates protect against false urgency

## License

Proprietary
