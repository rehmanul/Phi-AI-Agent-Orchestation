"""
Mermaid Diagrams API

Serves Mermaid diagram files for visualization.
"""

import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/diagrams", tags=["diagrams"])

# Diagram directories to search
DIAGRAM_DIRS = [
    Path("Filesss"),
    Path("diagrams"),
    Path("docs/diagrams"),
]

# Pydantic models
class DiagramInfo(BaseModel):
    name: str
    filename: str
    path: str
    size_bytes: int

class DiagramContent(BaseModel):
    name: str
    content: str
    filename: str

def _find_diagrams() -> List[dict]:
    """Find all .mmd files in the diagram directories."""
    diagrams = []
    
    for dir_path in DIAGRAM_DIRS:
        if not dir_path.exists():
            continue
        
        for mmd_file in dir_path.glob("*.mmd"):
            # Create a clean name from filename
            name = mmd_file.stem.replace("_", " ").replace("-", " ").title()
            
            diagrams.append({
                "name": name,
                "filename": mmd_file.name,
                "path": str(mmd_file),
                "size_bytes": mmd_file.stat().st_size,
            })
    
    return sorted(diagrams, key=lambda x: x["name"])

@router.get("/")
async def list_diagrams():
    """List all available Mermaid diagrams."""
    diagrams = _find_diagrams()
    return {"diagrams": diagrams, "count": len(diagrams)}

@router.get("/{filename}")
async def get_diagram(filename: str):
    """Get a specific diagram's content."""
    # Find the diagram file
    diagram_path = None
    for dir_path in DIAGRAM_DIRS:
        potential_path = dir_path / filename
        if potential_path.exists():
            diagram_path = potential_path
            break
    
    if not diagram_path:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    try:
        with open(diagram_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading diagram: {str(e)}")
    
    name = diagram_path.stem.replace("_", " ").replace("-", " ").title()
    
    return DiagramContent(
        name=name,
        content=content,
        filename=filename,
    )

@router.get("/by-state/{state}")
async def get_diagrams_for_state(state: str):
    """Get diagrams relevant to a legislative state."""
    diagrams = _find_diagrams()
    
    # Filter by state keyword (case insensitive)
    state_lower = state.lower().replace("_", " ")
    relevant = [
        d for d in diagrams 
        if state_lower in d["name"].lower() or state_lower in d["filename"].lower()
    ]
    
    return {"state": state, "diagrams": relevant}
