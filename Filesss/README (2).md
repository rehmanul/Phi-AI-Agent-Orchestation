# Investment Sales BD System

A minimal MVP system for identifying likely sellers in investment sales through data intake, normalization, scoring, and call list generation.

## Architecture

The system follows a clear data flow:

1. **Intake** → Raw CSV/JSON files uploaded and registered
2. **Normalization** → Owner entity matching, asset mapping, hold period calculation
3. **Scoring** → Heuristic-based sell probability scoring with confidence metadata
4. **Call List Generation** → Deterministic ranking and filtering
5. **Review & Approval** → Human-gated approval workflow
6. **Execution** → Approved call list ready for outreach

## Directory Structure

```
investment-sales-bd/
├── api/
│   ├── models/          # Pydantic data models
│   └── routes/          # API endpoints
├── agents/
│   ├── normalization/   # Owner/asset normalization
│   ├── scoring/         # Sell probability scoring
│   ├── execution/       # Call list generation
│   └── utils/           # Lineage logging
├── data/
│   ├── raw/             # Immutable source files
│   ├── normalized/      # Structured outputs
│   ├── scored/          # AI/heuristic outputs
│   ├── execution/       # Approved outputs
│   └── logs/            # Lineage, approvals
├── schemas/              # Frozen schemas
├── config/               # YAML configs
└── frontend/             # Next.js UI
```

## Setup

### Backend

```bash
cd investment-sales-bd
pip install -r requirements.txt
python -m api.main
```

API will be available at `http://localhost:8000`

### Frontend

```bash
cd investment-sales-bd/frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

### Intake
- `POST /api/bd/intake/owners` - Upload owner list
- `POST /api/bd/intake/deals` - Upload deal history
- `POST /api/bd/intake/market` - Upload market data
- `POST /api/bd/intake/debt` - Upload debt feeds
- `GET /api/bd/intake/sources` - List all sources

### Targets
- `GET /api/bd/targets/pending` - Get pending targets
- `GET /api/bd/targets/approved` - Get approved call list
- `GET /api/bd/targets/{target_id}` - Get target details
- `POST /api/bd/targets/{target_id}/approve` - Approve target
- `POST /api/bd/targets/{target_id}/reject` - Reject target

## Workflow

1. **Upload Data**: Use `/bd/intake` to upload owner lists, deal history, market data, and debt feeds
2. **Run Normalization**: Normalize owners, map assets, calculate hold periods
3. **Run Scoring**: Score sell probability using heuristics
4. **Generate Call List**: Create ranked list of targets
5. **Review**: Use `/bd/targets` to review and approve/reject targets
6. **Call List**: View approved targets at `/bd/call-list` and export to CSV

## Configuration

Edit YAML files in `config/`:
- `scoring_weights.yaml` - Scoring factor weights
- `confidence_thresholds.yaml` - Minimum thresholds
- `approval_rules.yaml` - Review requirements

## Data Governance

- All source files are hashed and registered
- Lineage tracking logs all transformations
- Schemas are frozen in `schemas/`
- All outputs are reproducible from lineage logs

## Notes

- This is a minimal MVP - production would require database, authentication, and additional features
- Scoring uses heuristics - outputs require human review
- All AI/heuristic outputs are flagged for review before execution
