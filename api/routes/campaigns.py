"""
Campaigns API Routes
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Campaign, get_async_db

router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    goal: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    status: Optional[str] = None
    keywords: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class CampaignResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    goal: Optional[str]
    status: str
    keywords: List[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_async_db),
):
    """List all campaigns."""
    query = select(Campaign).offset(offset).limit(limit)
    
    if status:
        query = query.where(Campaign.status == status)
    
    query = query.order_by(Campaign.created_at.desc())
    
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new campaign."""
    campaign = Campaign(
        name=data.name,
        description=data.description,
        goal=data.goal,
        keywords=data.keywords,
        settings=data.settings,
        status="active",
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """Update a campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Archive a campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.status = "archived"
    await db.commit()
    
    return {"status": "archived"}
