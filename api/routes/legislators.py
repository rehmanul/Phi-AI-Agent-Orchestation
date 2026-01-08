"""
Legislators API Routes
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Legislator, get_async_db

router = APIRouter()


class LegislatorResponse(BaseModel):
    id: UUID
    bioguide_id: Optional[str]
    first_name: str
    last_name: str
    full_name: str
    party: str
    chamber: str
    state: str
    district: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    twitter_handle: Optional[str]
    stance: str
    committees: List[str]

    class Config:
        from_attributes = True


class LegislatorUpdate(BaseModel):
    stance: Optional[str] = None
    notes: Optional[str] = None


@router.get("/", response_model=List[LegislatorResponse])
async def list_legislators(
    chamber: Optional[str] = Query(None),
    party: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    stance: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_async_db),
):
    """List legislators with filters."""
    query = select(Legislator).offset(offset).limit(limit)
    
    filters = []
    if chamber:
        filters.append(Legislator.chamber == chamber)
    if party:
        filters.append(Legislator.party == party)
    if state:
        filters.append(Legislator.state == state)
    if stance:
        filters.append(Legislator.stance == stance)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Legislator.state, Legislator.last_name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{legislator_id}", response_model=LegislatorResponse)
async def get_legislator(
    legislator_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific legislator."""
    result = await db.execute(
        select(Legislator).where(Legislator.id == legislator_id)
    )
    legislator = result.scalar()
    
    if not legislator:
        raise HTTPException(status_code=404, detail="Legislator not found")
    
    return legislator


@router.put("/{legislator_id}", response_model=LegislatorResponse)
async def update_legislator(
    legislator_id: UUID,
    data: LegislatorUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """Update legislator info (mainly stance and notes)."""
    result = await db.execute(
        select(Legislator).where(Legislator.id == legislator_id)
    )
    legislator = result.scalar()
    
    if not legislator:
        raise HTTPException(status_code=404, detail="Legislator not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(legislator, field, value)
    
    await db.commit()
    await db.refresh(legislator)
    
    return legislator


@router.get("/stats/by-stance")
async def get_stance_breakdown(
    db: AsyncSession = Depends(get_async_db),
):
    """Get breakdown of legislators by stance."""
    from sqlalchemy import func
    
    result = await db.execute(
        select(
            Legislator.stance,
            func.count(Legislator.id)
        ).group_by(Legislator.stance)
    )
    
    return {row[0]: row[1] for row in result.all()}


@router.get("/stats/by-party")
async def get_party_breakdown(
    db: AsyncSession = Depends(get_async_db),
):
    """Get breakdown of legislators by party."""
    from sqlalchemy import func
    
    result = await db.execute(
        select(
            Legislator.party,
            func.count(Legislator.id)
        ).group_by(Legislator.party)
    )
    
    return {row[0]: row[1] for row in result.all()}
