"""
Content API Routes
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import ContentItem, get_async_db

router = APIRouter()


class ContentResponse(BaseModel):
    id: UUID
    campaign_id: Optional[UUID]
    content_type: str
    title: Optional[str]
    body: str
    summary: Optional[str]
    hashtags: List[str]
    status: str
    target_platform: Optional[str]
    performance_score: Optional[float]
    created_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class ContentCreate(BaseModel):
    campaign_id: Optional[UUID] = None
    content_type: str
    title: Optional[str] = None
    body: str
    hashtags: List[str] = Field(default_factory=list)
    target_platform: Optional[str] = None


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None
    hashtags: Optional[List[str]] = None


@router.get("/", response_model=List[ContentResponse])
async def list_content(
    content_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    campaign_id: Optional[UUID] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_async_db),
):
    """List content items."""
    query = select(ContentItem).offset(offset).limit(limit)
    
    filters = []
    if content_type:
        filters.append(ContentItem.content_type == content_type)
    if status:
        filters.append(ContentItem.status == status)
    if campaign_id:
        filters.append(ContentItem.campaign_id == campaign_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(ContentItem.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific content item."""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    content = result.scalar()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content


@router.post("/", response_model=ContentResponse)
async def create_content(
    data: ContentCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new content item."""
    content = ContentItem(
        campaign_id=data.campaign_id,
        content_type=data.content_type,
        title=data.title,
        body=data.body,
        hashtags=data.hashtags,
        target_platform=data.target_platform,
        status="draft",
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    
    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    data: ContentUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """Update a content item."""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    content = result.scalar()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(content, field, value)
    
    await db.commit()
    await db.refresh(content)
    
    return content


@router.post("/{content_id}/approve")
async def approve_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Approve content for publishing."""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    content = result.scalar()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = "approved"
    content.approved_at = datetime.utcnow()
    await db.commit()
    
    return {"status": "approved"}


@router.post("/{content_id}/publish")
async def publish_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Mark content as published."""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    content = result.scalar()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = "published"
    content.published_at = datetime.utcnow()
    await db.commit()
    
    return {"status": "published"}
