"""
Agents Control API Routes
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.messaging import AgentMessage, KafkaProducer, Topics, get_producer

router = APIRouter()


class AgentCommand(BaseModel):
    command: str
    payload: Dict[str, Any] = {}


class ScanCommand(BaseModel):
    scan_type: str = "all"  # all, legislative, news, social


class ContentRequest(BaseModel):
    content_type: str
    params: Dict[str, Any] = {}


@router.get("/status")
async def get_agents_status():
    """Get status of all agents."""
    # In production, this would query actual agent status from Redis or similar
    return {
        "monitoring": {"status": "running", "last_activity": None},
        "analysis": {"status": "running", "last_activity": None},
        "strategy": {"status": "running", "last_activity": None},
        "tactics": {"status": "running", "last_activity": None},
        "content": {"status": "running", "last_activity": None},
        "distribution": {"status": "running", "last_activity": None},
        "feedback": {"status": "running", "last_activity": None},
    }


@router.post("/monitoring/scan")
async def trigger_scan(data: ScanCommand):
    """Trigger a monitoring scan."""
    producer = await get_producer()
    
    await producer.send(
        Topics.COMMANDS,
        AgentMessage(
            type="scan_command",
            source_agent="api",
            target_agent="monitoring",
            payload={"scan_type": data.scan_type},
        ),
    )
    
    return {"status": "scan_triggered", "scan_type": data.scan_type}


@router.post("/analysis/brief")
async def generate_brief(hours: int = 24):
    """Generate an intelligence brief."""
    producer = await get_producer()
    
    await producer.send(
        Topics.COMMANDS,
        AgentMessage(
            type="generate_brief",
            source_agent="api",
            target_agent="analysis",
            payload={"period_hours": hours},
        ),
    )
    
    return {"status": "brief_requested", "period_hours": hours}


@router.post("/content/generate")
async def generate_content(data: ContentRequest):
    """Request content generation."""
    producer = await get_producer()
    
    await producer.send(
        Topics.CONTENT,
        AgentMessage(
            type="generate_content",
            source_agent="api",
            target_agent="content",
            payload={
                "content_type": data.content_type,
                "params": data.params,
            },
        ),
    )
    
    return {"status": "content_requested", "content_type": data.content_type}


@router.post("/strategy/update")
async def request_strategy_update(
    campaign_id: Optional[str] = None,
    new_information: Dict[str, Any] = {},
):
    """Request strategy update."""
    producer = await get_producer()
    
    await producer.send(
        Topics.STRATEGY,
        AgentMessage(
            type="update_strategy",
            source_agent="api",
            target_agent="strategy",
            payload={
                "campaign_id": campaign_id,
                "new_information": new_information,
            },
        ),
    )
    
    return {"status": "strategy_update_requested"}


@router.post("/feedback/report")
async def generate_report(hours: int = 24, campaign_id: Optional[str] = None):
    """Generate a performance report."""
    producer = await get_producer()
    
    await producer.send(
        Topics.FEEDBACK,
        AgentMessage(
            type="generate_report",
            source_agent="api",
            target_agent="feedback",
            payload={
                "period_hours": hours,
                "campaign_id": campaign_id,
            },
        ),
    )
    
    return {"status": "report_requested", "period_hours": hours}
