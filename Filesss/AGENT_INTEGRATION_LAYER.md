# Agent Integration Layer

## Overview

The Agent Integration Layer connects existing agent files in `agents/` to the orchestrator API, enabling end-to-end workflows where agents can submit artifacts and query workflow state.

## Architecture

### Components

1. **AgentRunner** (`app/agent_runner.py`)
   - Loads and executes agent modules dynamically
   - Submits agent outputs as artifacts via AgentClient
   - Handles errors gracefully without corrupting orchestrator state
   - Maps agent IDs to artifact names and review gates

2. **AgentSpawner** (`app/agent_spawner.py`)
   - Reads agent registry (`registry/agent-registry.json`)
   - Filters agents by current legislative state
   - Spawns agents via AgentRunner
   - Manages basic agent lifecycle

### Key Design Principles

- **Isolation**: Agents run in separate processes; failures don't affect orchestrator
- **Client Pattern**: Agents are clients of the API, not part of core logic
- **Error Handling**: All agent errors are caught and logged, never crash orchestrator
- **State Mapping**: Agent outputs are automatically mapped to artifact names and review gates

## Usage

### Spawning a Single Agent

```python
from app.agent_spawner import AgentSpawner

spawner = AgentSpawner(workflow_id="workflow-123")
result = spawner.spawn_agent(
    agent_id="draft_concept_memo_pre_evt",
    agent_type="Drafting",
    scope="Generate Concept Memo",
    risk_level="MEDIUM"
)
```

### Spawning Agents for Current State

```python
from app.agent_spawner import AgentSpawner
from app.models import LegislativeState

spawner = AgentSpawner(workflow_id="workflow-123")
results = spawner.spawn_agents_for_state(
    legislative_state=LegislativeState.PRE_EVT,
    agent_types=["Intelligence", "Drafting"]  # Optional filter
)
```

### API Endpoints

- `POST /api/v1/workflows/{workflow_id}/agents/spawn` - Spawn a single agent
- `POST /api/v1/workflows/{workflow_id}/agents/spawn-for-state` - Spawn all agents for current state

## Agent Output Mapping

Agents generate JSON files that are automatically mapped to artifact names:

| Agent ID | Artifact Name | Review Gate |
|----------|---------------|-------------|
| `draft_concept_memo_pre_evt` | Concept Memo | HR_PRE |
| `draft_framing_intro_evt` | Legitimacy & Policy Framing | HR_PRE |
| `draft_whitepaper_intro_evt` | Policy Whitepaper | HR_PRE |
| `intel_stakeholder_map_pre_evt` | Stakeholder Landscape Map | None |

## Error Handling

- Agent execution failures are caught and logged
- Failed agents return error details but don't crash the orchestrator
- API submission failures are handled gracefully
- All errors include correlation IDs for tracing

## Testing

Run agent integration tests:

```bash
python -m pytest tests/test_agent_integration.py -v
```

## Constraints

- Agents must have a `main()` function that returns a file path
- Agent output files must be valid JSON
- Agents are read-only clients; they cannot modify orchestrator state directly
- All state changes go through the API
