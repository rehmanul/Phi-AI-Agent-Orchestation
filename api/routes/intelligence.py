"""
Intelligence API Routes
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import IntelligenceItem, get_async_db

router = APIRouter()


class IntelligenceResponse(BaseModel):
    id: UUID
    source_type: str
    source_name: Optional[str]
    source_url: Optional[str]
    title: Optional[str]
    content: Optional[str]
    summary: Optional[str]
    author: Optional[str]
    relevance_score: float
    sentiment_score: Optional[float]
    is_opposition: bool
    requires_response: bool
    priority: int
    status: str
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[IntelligenceResponse])
async def list_intelligence(
    source_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_opposition: Optional[bool] = Query(None),
    min_relevance: Optional[float] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_async_db),
):
    """List intelligence items with filters."""
    query = select(IntelligenceItem).offset(offset).limit(limit)
    
    filters = []
    if source_type:
        filters.append(IntelligenceItem.source_type == source_type)
    if status:
        filters.append(IntelligenceItem.status == status)
    if is_opposition is not None:
        filters.append(IntelligenceItem.is_opposition == is_opposition)
    if min_relevance:
        filters.append(IntelligenceItem.relevance_score >= min_relevance)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(IntelligenceItem.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{item_id}", response_model=IntelligenceResponse)
async def get_intelligence_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific intelligence item."""
    result = await db.execute(
        select(IntelligenceItem).where(IntelligenceItem.id == item_id)
    )
    item = result.scalar()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.put("/{item_id}/status")
async def update_status(
    item_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Update intelligence item status."""
    result = await db.execute(
        select(IntelligenceItem).where(IntelligenceItem.id == item_id)
    )
    item = result.scalar()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.status = status
    await db.commit()
    
    return {"status": status}


@router.get("/stats/summary")
async def get_intelligence_stats(
    db: AsyncSession = Depends(get_async_db),
):
    """Get intelligence summary statistics."""
    from sqlalchemy import func
    
    # Total counts by source
    source_counts = await db.execute(
        select(
            IntelligenceItem.source_type,
            func.count(IntelligenceItem.id)
        ).group_by(IntelligenceItem.source_type)
    )
    
    by_source = {row[0]: row[1] for row in source_counts.all()}
    
    # Opposition count
    opp_result = await db.execute(
        select(func.count(IntelligenceItem.id)).where(
            IntelligenceItem.is_opposition == True
        )
    )
    opposition_count = opp_result.scalar() or 0
    
    # High priority count
    priority_result = await db.execute(
        select(func.count(IntelligenceItem.id)).where(
            IntelligenceItem.priority >= 7
        )
    )
    high_priority = priority_result.scalar() or 0
    
    return {
        "by_source": by_source,
        "opposition_count": opposition_count,
        "high_priority_count": high_priority,
        "total": sum(by_source.values()),
    }
