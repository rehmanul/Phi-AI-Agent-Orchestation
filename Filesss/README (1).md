# Wi-Charge OEM Risk Proposal Generator

A system for processing OEM PDFs and generating risk proposals for Wi-Charge wireless power integration.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python pipeline/main.py --input-dir ./input_pdfs --output-dir ./output
```

## Directory Structure

```
wi-charge-oem-risk-system/
├── pipeline/           # Main processing pipeline
├── agents/             # AI agents and personas
├── extractors/         # Data extraction modules
├── models/             # Risk models and training
├── review/             # Human review interfaces
├── outputs/            # Generated artifacts
└── logs/               # Execution logs
```

## System Components

See [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) for detailed architecture.
