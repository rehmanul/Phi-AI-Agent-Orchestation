"""
Metrics API Routes
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Metric, Action, ContentItem, IntelligenceItem, get_async_db

router = APIRouter()


class MetricResponse(BaseModel):
    id: UUID
    campaign_id: Optional[UUID]
    metric_type: str
    metric_name: str
    value: float
    dimensions: Dict[str, Any]
    recorded_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    intelligence_total: int
    intelligence_today: int
    content_total: int
    content_published: int
    actions_pending: int
    actions_completed: int
    opposition_alerts: int


@router.get("/", response_model=List[MetricResponse])
async def list_metrics(
    metric_type: Optional[str] = Query(None),
    campaign_id: Optional[UUID] = Query(None),
    hours: int = Query(24, le=168),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_async_db),
):
    """List metrics with filters."""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(Metric).where(
        Metric.recorded_at >= since
    ).limit(limit)
    
    if metric_type:
        query = query.where(Metric.metric_type == metric_type)
    if campaign_id:
        query = query.where(Metric.campaign_id == campaign_id)
    
    query = query.order_by(Metric.recorded_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_async_db),
):
    """Get dashboard statistics."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Intelligence stats
    intel_total = await db.execute(
        select(func.count(IntelligenceItem.id))
    )
    intel_today = await db.execute(
        select(func.count(IntelligenceItem.id)).where(
            IntelligenceItem.created_at >= today
        )
    )
    opposition = await db.execute(
        select(func.count(IntelligenceItem.id)).where(
            IntelligenceItem.is_opposition == True,
            IntelligenceItem.status == "new",
        )
    )
    
    # Content stats
    content_total = await db.execute(
        select(func.count(ContentItem.id))
    )
    content_published = await db.execute(
        select(func.count(ContentItem.id)).where(
            ContentItem.status == "published"
        )
    )
    
    # Action stats
    actions_pending = await db.execute(
        select(func.count(Action.id)).where(
            Action.status == "pending"
        )
    )
    actions_completed = await db.execute(
        select(func.count(Action.id)).where(
            Action.status == "completed"
        )
    )
    
    return DashboardStats(
        intelligence_total=intel_total.scalar() or 0,
        intelligence_today=intel_today.scalar() or 0,
        content_total=content_total.scalar() or 0,
        content_published=content_published.scalar() or 0,
        actions_pending=actions_pending.scalar() or 0,
        actions_completed=actions_completed.scalar() or 0,
        opposition_alerts=opposition.scalar() or 0,
    )


@router.get("/timeline")
async def get_metrics_timeline(
    metric_type: str = Query(...),
    hours: int = Query(24, le=168),
    interval_minutes: int = Query(60, ge=15, le=1440),
    db: AsyncSession = Depends(get_async_db),
):
    """Get metrics timeline for charts."""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Get all metrics in range
    result = await db.execute(
        select(Metric).where(
            Metric.metric_type == metric_type,
            Metric.recorded_at >= since,
        ).order_by(Metric.recorded_at)
    )
    metrics = result.scalars().all()
    
    # Bucket by interval
    buckets: Dict[str, float] = {}
    for metric in metrics:
        bucket_time = metric.recorded_at.replace(
            minute=(metric.recorded_at.minute // interval_minutes) * interval_minutes,
            second=0,
            microsecond=0,
        )
        key = bucket_time.isoformat()
        buckets[key] = buckets.get(key, 0) + metric.value
    
    return {
        "metric_type": metric_type,
        "interval_minutes": interval_minutes,
        "data": [
            {"timestamp": k, "value": v}
            for k, v in sorted(buckets.items())
        ],
    }
