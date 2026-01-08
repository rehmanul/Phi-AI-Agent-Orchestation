"""
SQLAlchemy Database Models

Defines all database tables for the advocacy orchestration system.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    type_annotation_map = {
        Dict[str, Any]: JSONB,
        List[Any]: JSONB,
    }


# =============================================================================
# Campaigns
# =============================================================================

class Campaign(Base):
    """
    Represents an advocacy campaign.
    
    A campaign is the top-level container for all advocacy activities
    around a specific issue or bill.
    """
    
    __tablename__ = "campaigns"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    goal: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        index=True,
    )  # active, paused, completed, archived
    
    # Campaign configuration
    settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    keywords: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    bills: Mapped[List["Bill"]] = relationship(
        "Bill",
        secondary="campaign_bills",
        back_populates="campaigns",
    )
    content_items: Mapped[List["ContentItem"]] = relationship(
        "ContentItem",
        back_populates="campaign",
    )
    actions: Mapped[List["Action"]] = relationship("Action", back_populates="campaign")
    metrics: Mapped[List["Metric"]] = relationship("Metric", back_populates="campaign")


# =============================================================================
# Bills and Legislation
# =============================================================================

class Bill(Base):
    """
    Represents a legislative bill being tracked.
    """
    
    __tablename__ = "bills"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )  # Congress.gov ID
    
    number: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    full_text_url: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), index=True)  # introduced, committee, passed, etc.
    chamber: Mapped[str] = mapped_column(String(20))  # house, senate
    congress: Mapped[Optional[int]] = mapped_column(Integer)  # 118th, 119th, etc.
    
    # Dates
    introduced_date: Mapped[Optional[datetime]] = mapped_column(Date)
    last_action_date: Mapped[Optional[datetime]] = mapped_column(Date)
    last_action: Mapped[Optional[str]] = mapped_column(Text)
    
    # Additional data
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    sponsors: Mapped[List[str]] = mapped_column(JSONB, default=list)
    cosponsors_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Relationships
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign",
        secondary="campaign_bills",
        back_populates="bills",
    )


class CampaignBill(Base):
    """Association table for campaigns and bills."""
    
    __tablename__ = "campaign_bills"
    
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        primary_key=True,
    )
    bill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# Legislators
# =============================================================================

class Legislator(Base):
    """
    Represents an elected official / legislator.
    """
    
    __tablename__ = "legislators"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    bioguide_id: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        index=True,
    )
    
    # Basic info
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    
    party: Mapped[str] = mapped_column(String(50), index=True)  # D, R, I
    chamber: Mapped[str] = mapped_column(String(20), index=True)  # house, senate
    state: Mapped[str] = mapped_column(String(2), index=True)
    district: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Contact info
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(Text)
    office_address: Mapped[Optional[str]] = mapped_column(Text)
    
    # Social media
    twitter_handle: Mapped[Optional[str]] = mapped_column(String(100))
    facebook_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Campaign-specific stance
    stance: Mapped[str] = mapped_column(
        String(50),
        default="unknown",
    )  # support, oppose, neutral, unknown
    
    # Committee memberships and other data
    committees: Mapped[List[str]] = mapped_column(JSONB, default=list)
    leadership_positions: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Notes and metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    __table_args__ = (
        Index("ix_legislators_state_chamber", "state", "chamber"),
    )


# =============================================================================
# Intelligence Items (Monitoring)
# =============================================================================

class IntelligenceItem(Base):
    """
    An item of intelligence gathered by the monitoring agent.
    
    Could be a news article, social media post, regulatory filing, etc.
    """
    
    __tablename__ = "intelligence_items"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Source information
    source_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )  # news, twitter, reddit, legislative, regulatory
    source_name: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    
    # Content
    title: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Analysis
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)  # -1 to 1
    entities: Mapped[List[str]] = mapped_column(JSONB, default=list)
    keywords: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Classification
    is_opposition: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    requires_response: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="new",
        index=True,
    )  # new, reviewed, actioned, archived
    
    # Timestamps
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Additional metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_intelligence_source_published", "source_type", "published_at"),
    )


# =============================================================================
# Claims (Fact-Checking)
# =============================================================================

class Claim(Base):
    """
    A claim to be fact-checked.
    
    Tracks claims made by opposition or in media for verification.
    """
    
    __tablename__ = "claims"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_author: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Verification
    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True,
    )  # pending, verified_true, verified_false, misleading, needs_context
    verdict: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Evidence
    evidence: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    rebuttal: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)


# =============================================================================
# Content Items
# =============================================================================

class ContentItem(Base):
    """
    Content created by the content agents.
    
    Includes press releases, social posts, emails, fact sheets, etc.
    """
    
    __tablename__ = "content_items"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        index=True,
    )
    
    # Content type and metadata
    content_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )  # press_release, tweet, email, fact_sheet, op_ed, testimony, etc.
    title: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Content body
    body: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # For social media
    hashtags: Mapped[List[str]] = mapped_column(JSONB, default=list)
    mentions: Mapped[List[str]] = mapped_column(JSONB, default=list)
    media_urls: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Targeting
    target_audience: Mapped[Optional[str]] = mapped_column(String(255))
    target_platform: Mapped[Optional[str]] = mapped_column(String(50))
    target_legislator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("legislators.id", ondelete="SET NULL"),
    )
    
    # Status workflow
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        index=True,
    )  # draft, pending_review, approved, published, archived
    
    # A/B testing
    variant: Mapped[Optional[str]] = mapped_column(String(50))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="SET NULL"),
    )
    
    # Performance
    performance_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    campaign: Mapped[Optional["Campaign"]] = relationship(
        "Campaign",
        back_populates="content_items",
    )


# =============================================================================
# Actions (Tactics)
# =============================================================================

class Action(Base):
    """
    A tactical action to be executed.
    
    Generated by the tactics agent, executed by humans or distribution agent.
    """
    
    __tablename__ = "actions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        index=True,
    )
    
    # Action details
    action_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )  # phone_bank, letter_campaign, lobby_day, social_blitz, press_event, etc.
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    
    # Targeting
    target_legislators: Mapped[List[str]] = mapped_column(JSONB, default=list)
    target_regions: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Resources
    estimated_time_hours: Mapped[Optional[float]] = mapped_column(Float)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    volunteers_needed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Priority and scoring
    priority: Mapped[int] = mapped_column(Integer, default=5, index=True)  # 1-10
    impact_score: Mapped[Optional[float]] = mapped_column(Float)
    effort_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True,
    )  # pending, in_progress, completed, cancelled
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(Date)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Relationships
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="actions")


# =============================================================================
# Metrics
# =============================================================================

class Metric(Base):
    """
    Campaign metrics and analytics.
    
    Tracked by the feedback agent.
    """
    
    __tablename__ = "metrics"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        index=True,
    )
    
    # Metric identification
    metric_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )  # email_open_rate, social_engagement, calls_made, cosponsors_gained, etc.
    metric_name: Mapped[str] = mapped_column(String(255))
    
    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    previous_value: Mapped[Optional[float]] = mapped_column(Float)
    target_value: Mapped[Optional[float]] = mapped_column(Float)
    
    # Dimensions for grouping
    dimensions: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Time period
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )
    
    # Relationships
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="metrics")
    
    __table_args__ = (
        Index("ix_metrics_campaign_type_time", "campaign_id", "metric_type", "recorded_at"),
    )


# =============================================================================
# Supporters
# =============================================================================

class Supporter(Base):
    """
    A campaign supporter / volunteer.
    """
    
    __tablename__ = "supporters"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Contact info
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Location
    state: Mapped[Optional[str]] = mapped_column(String(2), index=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(10))
    congressional_district: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Engagement
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    actions_taken: Mapped[int] = mapped_column(Integer, default=0)
    last_action_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Communication preferences
    email_opted_in: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_opted_in: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Tags and segments
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)


# =============================================================================
# Agent Events (Audit Log)
# =============================================================================

class AgentEvent(Base):
    """
    Audit log of agent activities.
    
    Tracks what each agent did for debugging and compliance.
    """
    
    __tablename__ = "agent_events"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    agent_type: Mapped[str] = mapped_column(String(50), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    
    # Event details
    description: Mapped[str] = mapped_column(Text)
    input_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    output_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    
    # Status and errors
    status: Mapped[str] = mapped_column(String(50))  # success, error, partial
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Cost tracking (for LLM calls)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("ix_agent_events_agent_time", "agent_type", "created_at"),
    )


# =============================================================================
# System Settings (Encrypted Configuration)
# =============================================================================

class SystemSetting(Base):
    """
    Encrypted system settings and API keys.
    
    Stores configuration that can be modified at runtime.
    All sensitive values are encrypted using Fernet.
    """
    
    __tablename__ = "system_settings"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Setting identification
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )  # llm, external_api, communication, messaging, general
    
    # Value storage
    value: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted
    is_secret: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Validation
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_regex: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Status
    is_configured: Mapped[bool] = mapped_column(Boolean, default=False)
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
