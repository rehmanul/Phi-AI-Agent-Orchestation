"""
Legislative State Management API

Manages the legislative spine with 6 states:
PRE_EVT → INTRO_EVT → COMM_EVT → FLOOR_EVT → FINAL_EVT → IMPL_EVT
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/legislative", tags=["legislative"])

# State definitions
class LegislativeState(str, Enum):
    PRE_EVT = "PRE_EVT"
    INTRO_EVT = "INTRO_EVT"
    COMM_EVT = "COMM_EVT"
    FLOOR_EVT = "FLOOR_EVT"
    FINAL_EVT = "FINAL_EVT"
    IMPL_EVT = "IMPL_EVT"

STATE_ORDER = [
    LegislativeState.PRE_EVT,
    LegislativeState.INTRO_EVT,
    LegislativeState.COMM_EVT,
    LegislativeState.FLOOR_EVT,
    LegislativeState.FINAL_EVT,
    LegislativeState.IMPL_EVT,
]

STATE_DESCRIPTIONS = {
    "PRE_EVT": {"name": "Policy Opportunity Detected", "icon": "🔍", "description": "Signal scanning, stakeholder mapping, staff education"},
    "INTRO_EVT": {"name": "Bill Vehicle Identified", "icon": "📜", "description": "Sponsor targeting, framing, academic validation"},
    "COMM_EVT": {"name": "Committee Referral", "icon": "🏛️", "description": "Agenda analysis, briefings, draft language, amendments"},
    "FLOOR_EVT": {"name": "Floor Scheduled", "icon": "🗳️", "description": "Floor messaging, timing, media narrative"},
    "FINAL_EVT": {"name": "Vote Imminent", "icon": "⚡", "description": "Coalition activation, final constituent narrative"},
    "IMPL_EVT": {"name": "Law Enacted", "icon": "✅", "description": "Implementation guidance, oversight, outcome reporting"},
}

# Human review gates
REVIEW_GATES = {
    "HR_PRE": {"from_state": "PRE_EVT", "to_state": "INTRO_EVT", "name": "Approve Concept Direction"},
    "HR_LANG": {"from_state": "COMM_EVT", "to_state": "FLOOR_EVT", "name": "Approve Legislative Language"},
    "HR_MSG": {"from_state": "FLOOR_EVT", "to_state": "FINAL_EVT", "name": "Approve Messaging & Narrative"},
    "HR_RELEASE": {"from_state": "FINAL_EVT", "to_state": "IMPL_EVT", "name": "Authorize Public Release"},
}

# Storage paths
DATA_DIR = Path("data")
STATE_FILE = DATA_DIR / "legislative-state.json"

# Pydantic models
class StateInfo(BaseModel):
    current_state: str
    state_name: str
    state_icon: str
    state_description: str
    state_index: int
    total_states: int
    can_advance: bool
    pending_gate: Optional[str] = None

class StateTransition(BaseModel):
    from_state: str
    to_state: str
    timestamp: str
    approved_by: Optional[str] = None
    gate_id: Optional[str] = None

class StateHistory(BaseModel):
    transitions: List[StateTransition]

class AdvanceRequest(BaseModel):
    approved_by: str
    notes: Optional[str] = None

class GateInfo(BaseModel):
    gate_id: str
    name: str
    from_state: str
    to_state: str
    status: str  # pending, approved, blocked
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None

# Storage functions
def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _load_state() -> dict:
    _ensure_data_dir()
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    # Initialize default state
    default = {
        "current_state": "PRE_EVT",
        "transitions": [],
        "gates": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    _save_state(default)
    return default

def _save_state(state: dict):
    _ensure_data_dir()
    state["updated_at"] = datetime.utcnow().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# API Endpoints
@router.get("/state", response_model=StateInfo)
async def get_current_state():
    """Get current legislative state."""
    state = _load_state()
    current = state.get("current_state", "PRE_EVT")
    info = STATE_DESCRIPTIONS.get(current, {})
    
    state_index = STATE_ORDER.index(LegislativeState(current))
    can_advance = state_index < len(STATE_ORDER) - 1
    
    # Check for pending gate
    pending_gate = None
    for gate_id, gate in REVIEW_GATES.items():
        if gate["from_state"] == current:
            gate_status = state.get("gates", {}).get(gate_id, {}).get("status", "pending")
            if gate_status == "pending":
                pending_gate = gate_id
                break
    
    return StateInfo(
        current_state=current,
        state_name=info.get("name", current),
        state_icon=info.get("icon", "📋"),
        state_description=info.get("description", ""),
        state_index=state_index,
        total_states=len(STATE_ORDER),
        can_advance=can_advance and pending_gate is None,
        pending_gate=pending_gate,
    )

@router.get("/states")
async def get_all_states():
    """Get all legislative states with descriptions."""
    state = _load_state()
    current = state.get("current_state", "PRE_EVT")
    current_index = STATE_ORDER.index(LegislativeState(current))
    
    states = []
    for i, s in enumerate(STATE_ORDER):
        info = STATE_DESCRIPTIONS.get(s.value, {})
        status = "completed" if i < current_index else ("current" if i == current_index else "upcoming")
        states.append({
            "state_id": s.value,
            "name": info.get("name", s.value),
            "icon": info.get("icon", "📋"),
            "description": info.get("description", ""),
            "status": status,
            "index": i,
        })
    return {"states": states}

@router.get("/history", response_model=StateHistory)
async def get_state_history():
    """Get state transition history."""
    state = _load_state()
    transitions = [StateTransition(**t) for t in state.get("transitions", [])]
    return StateHistory(transitions=transitions)

@router.post("/advance", response_model=StateInfo)
async def advance_state(request: AdvanceRequest):
    """Advance to next legislative state (requires gate approval)."""
    state = _load_state()
    current = state.get("current_state", "PRE_EVT")
    current_index = STATE_ORDER.index(LegislativeState(current))
    
    if current_index >= len(STATE_ORDER) - 1:
        raise HTTPException(status_code=400, detail="Already at final state")
    
    # Check for pending gate
    for gate_id, gate in REVIEW_GATES.items():
        if gate["from_state"] == current:
            gate_status = state.get("gates", {}).get(gate_id, {}).get("status", "pending")
            if gate_status != "approved":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Gate {gate_id} must be approved before advancing"
                )
    
    next_state = STATE_ORDER[current_index + 1].value
    
    # Record transition
    transition = {
        "from_state": current,
        "to_state": next_state,
        "timestamp": datetime.utcnow().isoformat(),
        "approved_by": request.approved_by,
        "notes": request.notes,
    }
    state.setdefault("transitions", []).append(transition)
    state["current_state"] = next_state
    _save_state(state)
    
    return await get_current_state()

@router.get("/gates")
async def get_review_gates():
    """Get all review gates with their status."""
    state = _load_state()
    current = state.get("current_state", "PRE_EVT")
    
    gates = []
    for gate_id, gate in REVIEW_GATES.items():
        gate_state = state.get("gates", {}).get(gate_id, {})
        status = gate_state.get("status", "pending")
        
        # Determine if gate is active (current state matches from_state)
        is_active = gate["from_state"] == current
        
        gates.append({
            "gate_id": gate_id,
            "name": gate["name"],
            "from_state": gate["from_state"],
            "to_state": gate["to_state"],
            "status": status,
            "is_active": is_active,
            "approved_at": gate_state.get("approved_at"),
            "approved_by": gate_state.get("approved_by"),
        })
    
    return {"gates": gates}

@router.post("/gates/{gate_id}/approve")
async def approve_gate(gate_id: str, request: AdvanceRequest):
    """Approve a review gate."""
    if gate_id not in REVIEW_GATES:
        raise HTTPException(status_code=404, detail="Gate not found")
    
    state = _load_state()
    current = state.get("current_state", "PRE_EVT")
    gate = REVIEW_GATES[gate_id]
    
    if gate["from_state"] != current:
        raise HTTPException(
            status_code=400, 
            detail=f"Gate {gate_id} is not active for current state {current}"
        )
    
    state.setdefault("gates", {})[gate_id] = {
        "status": "approved",
        "approved_at": datetime.utcnow().isoformat(),
        "approved_by": request.approved_by,
        "notes": request.notes,
    }
    _save_state(state)
    
    return {"success": True, "gate_id": gate_id, "status": "approved"}

@router.post("/reset")
async def reset_state():
    """Reset to initial state (PRE_EVT)."""
    default = {
        "current_state": "PRE_EVT",
        "transitions": [],
        "gates": {},
        "created_at": datetime.utcnow().isoformat(),
    }
    _save_state(default)
    return {"success": True, "message": "State reset to PRE_EVT"}
