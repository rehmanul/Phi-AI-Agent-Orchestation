"""
Agent Orchestration API

Manages AI agent spawning, status, and artifacts.
Agent types: Intelligence, Drafting, Execution, Learning
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/orchestration", tags=["orchestration"])

# Agent types
class AgentType(str, Enum):
    INTELLIGENCE = "intelligence"
    DRAFTING = "drafting"
    EXECUTION = "execution"
    LEARNING = "learning"

# Agent definitions by state
AGENTS_BY_STATE = {
    "PRE_EVT": {
        "intelligence": ["signal_scan", "stakeholder_map"],
        "drafting": ["concept_memo"],
    },
    "INTRO_EVT": {
        "intelligence": ["signal_scan", "stakeholder_map", "opposition_detect"],
        "drafting": ["framing", "whitepaper"],
    },
    "COMM_EVT": {
        "intelligence": ["media_signal", "opposition_detect"],
        "drafting": ["language", "amendment_strategy"],
    },
    "FLOOR_EVT": {
        "intelligence": ["media_signal"],
        "drafting": ["messaging"],
        "execution": ["outreach", "coalition_activation"],
    },
    "FINAL_EVT": {
        "execution": ["outreach", "media_seeding", "counter_pressure"],
    },
    "IMPL_EVT": {
        "learning": ["causal_attribution", "strategy_reweighting"],
    },
}

AGENT_DESCRIPTIONS = {
    "signal_scan": {"name": "Signal Scan Agent", "icon": "📡", "description": "Scans industry, courts, agencies for policy signals"},
    "stakeholder_map": {"name": "Stakeholder Mapping Agent", "icon": "🗺️", "description": "Maps stakeholder landscape and relationships"},
    "opposition_detect": {"name": "Opposition Detection Agent", "icon": "🛑", "description": "Detects opposition framing and counter-narratives"},
    "media_signal": {"name": "Media Signal Monitor", "icon": "📰", "description": "Monitors media coverage and narrative trends"},
    "concept_memo": {"name": "Concept Memo Agent", "icon": "📄", "description": "Generates initial concept memos"},
    "framing": {"name": "Framing Agent", "icon": "🖼️", "description": "Develops legitimacy and policy framing"},
    "whitepaper": {"name": "Whitepaper Agent", "icon": "📋", "description": "Drafts policy whitepapers"},
    "language": {"name": "Legislative Language Agent", "icon": "📜", "description": "Drafts legislative language"},
    "amendment_strategy": {"name": "Amendment Strategy Agent", "icon": "✏️", "description": "Develops amendment strategies"},
    "messaging": {"name": "Messaging Draft Agent", "icon": "🗣️", "description": "Creates messaging and talking points"},
    "outreach": {"name": "Outreach Execution Agent", "icon": "📨", "description": "Executes staff briefings and outreach"},
    "coalition_activation": {"name": "Coalition Activation Agent", "icon": "🤝", "description": "Activates coalition partners"},
    "media_seeding": {"name": "Media Seeding Agent", "icon": "📰", "description": "Seeds narratives to media"},
    "counter_pressure": {"name": "Counter-Pressure Agent", "icon": "🧯", "description": "Deploys counter-pressure tactics"},
    "causal_attribution": {"name": "Causal Attribution Agent", "icon": "📐", "description": "Analyzes causal impact of tactics"},
    "strategy_reweighting": {"name": "Strategy Reweighting Agent", "icon": "🔁", "description": "Reweights strategies based on outcomes"},
}

# Storage paths
DATA_DIR = Path("data")
AGENTS_FILE = DATA_DIR / "spawned-agents.json"
ARTIFACTS_DIR = DATA_DIR / "artifacts"

# Pydantic models
class AgentInfo(BaseModel):
    agent_id: str
    agent_type: str
    name: str
    icon: str
    description: str
    status: str  # idle, running, completed, error
    spawned_at: Optional[str] = None
    completed_at: Optional[str] = None
    artifacts: List[str] = []

class SpawnRequest(BaseModel):
    agent_ids: List[str]

class SpawnResult(BaseModel):
    spawned: List[str]
    failed: List[str]

class ArtifactInfo(BaseModel):
    artifact_id: str
    agent_id: str
    artifact_type: str
    name: str
    created_at: str
    file_path: Optional[str] = None

# Storage functions
def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def _load_agents() -> dict:
    _ensure_dirs()
    if AGENTS_FILE.exists():
        with open(AGENTS_FILE, 'r') as f:
            return json.load(f)
    return {"agents": {}, "updated_at": None}

def _save_agents(data: dict):
    _ensure_dirs()
    data["updated_at"] = datetime.utcnow().isoformat()
    with open(AGENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# API Endpoints
@router.get("/agents")
async def list_agents(state: Optional[str] = None):
    """List all agents, optionally filtered by legislative state."""
    data = _load_agents()
    
    if state:
        # Get agents available for this state
        available = AGENTS_BY_STATE.get(state, {})
        agent_ids = []
        for agent_type, ids in available.items():
            agent_ids.extend(ids)
    else:
        # Get all known agents
        agent_ids = list(AGENT_DESCRIPTIONS.keys())
    
    agents = []
    for agent_id in agent_ids:
        info = AGENT_DESCRIPTIONS.get(agent_id, {})
        agent_data = data.get("agents", {}).get(agent_id, {})
        
        # Determine agent type
        agent_type = None
        for state_agents in AGENTS_BY_STATE.values():
            for atype, ids in state_agents.items():
                if agent_id in ids:
                    agent_type = atype
                    break
            if agent_type:
                break
        
        agents.append({
            "agent_id": agent_id,
            "agent_type": agent_type or "unknown",
            "name": info.get("name", agent_id),
            "icon": info.get("icon", "🤖"),
            "description": info.get("description", ""),
            "status": agent_data.get("status", "idle"),
            "spawned_at": agent_data.get("spawned_at"),
            "completed_at": agent_data.get("completed_at"),
            "artifacts": agent_data.get("artifacts", []),
        })
    
    return {"agents": agents}

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get details of a specific agent."""
    if agent_id not in AGENT_DESCRIPTIONS:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    data = _load_agents()
    info = AGENT_DESCRIPTIONS[agent_id]
    agent_data = data.get("agents", {}).get(agent_id, {})
    
    return {
        "agent_id": agent_id,
        "name": info.get("name", agent_id),
        "icon": info.get("icon", "🤖"),
        "description": info.get("description", ""),
        "status": agent_data.get("status", "idle"),
        "spawned_at": agent_data.get("spawned_at"),
        "completed_at": agent_data.get("completed_at"),
        "artifacts": agent_data.get("artifacts", []),
        "logs": agent_data.get("logs", []),
    }

@router.post("/spawn", response_model=SpawnResult)
async def spawn_agents(request: SpawnRequest):
    """Spawn one or more agents."""
    data = _load_agents()
    spawned = []
    failed = []
    
    for agent_id in request.agent_ids:
        if agent_id not in AGENT_DESCRIPTIONS:
            failed.append(agent_id)
            continue
        
        # Update agent status
        data.setdefault("agents", {})[agent_id] = {
            "status": "running",
            "spawned_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "artifacts": [],
            "logs": [
                {"timestamp": datetime.utcnow().isoformat(), "message": "Agent spawned"}
            ],
        }
        spawned.append(agent_id)
    
    _save_agents(data)
    return SpawnResult(spawned=spawned, failed=failed)

@router.post("/agents/{agent_id}/complete")
async def complete_agent(agent_id: str, artifacts: Optional[List[str]] = None):
    """Mark an agent as completed with optional artifacts."""
    data = _load_agents()
    
    if agent_id not in data.get("agents", {}):
        raise HTTPException(status_code=404, detail="Agent not spawned")
    
    data["agents"][agent_id]["status"] = "completed"
    data["agents"][agent_id]["completed_at"] = datetime.utcnow().isoformat()
    if artifacts:
        data["agents"][agent_id]["artifacts"] = artifacts
    data["agents"][agent_id]["logs"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Agent completed",
    })
    
    _save_agents(data)
    return {"success": True, "agent_id": agent_id}

@router.get("/artifacts")
async def list_artifacts():
    """List all artifacts from all agents."""
    _ensure_dirs()
    
    artifacts = []
    for agent_dir in ARTIFACTS_DIR.iterdir():
        if agent_dir.is_dir():
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    with open(artifact_file, 'r') as f:
                        artifact_data = json.load(f)
                    artifacts.append({
                        "artifact_id": artifact_file.stem,
                        "agent_id": agent_dir.name,
                        "name": artifact_data.get("name", artifact_file.stem),
                        "artifact_type": artifact_data.get("type", "unknown"),
                        "created_at": artifact_data.get("created_at", ""),
                        "file_path": str(artifact_file),
                    })
                except Exception:
                    pass
    
    return {"artifacts": artifacts}

@router.get("/artifacts/{agent_id}/{artifact_id}")
async def get_artifact(agent_id: str, artifact_id: str):
    """Get a specific artifact content."""
    artifact_path = ARTIFACTS_DIR / agent_id / f"{artifact_id}.json"
    
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    with open(artifact_path, 'r') as f:
        return json.load(f)

@router.get("/available-for-state/{state}")
async def get_agents_for_state(state: str):
    """Get agents available for a specific legislative state."""
    agents_by_type = AGENTS_BY_STATE.get(state, {})
    
    result = {}
    for agent_type, agent_ids in agents_by_type.items():
        result[agent_type] = []
        for agent_id in agent_ids:
            info = AGENT_DESCRIPTIONS.get(agent_id, {})
            result[agent_type].append({
                "agent_id": agent_id,
                "name": info.get("name", agent_id),
                "icon": info.get("icon", "🤖"),
                "description": info.get("description", ""),
            })
    
    return {"state": state, "agents": result}
