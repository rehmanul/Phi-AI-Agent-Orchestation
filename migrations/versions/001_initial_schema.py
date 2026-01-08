"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-01-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Campaigns
    op.create_table('campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('settings', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('keywords', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])

    # Bills
    op.create_table('bills',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('external_id', sa.String(100), nullable=True),
        sa.Column('number', sa.String(50), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('full_text_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('chamber', sa.String(20), nullable=False),
        sa.Column('congress', sa.Integer(), nullable=True),
        sa.Column('introduced_date', sa.Date(), nullable=True),
        sa.Column('last_action_date', sa.Date(), nullable=True),
        sa.Column('last_action', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('sponsors', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('cosponsors_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index('ix_bills_number', 'bills', ['number'])
    op.create_index('ix_bills_status', 'bills', ['status'])
    op.create_index('ix_bills_external_id', 'bills', ['external_id'])

    # Campaign-Bills association
    op.create_table('campaign_bills',
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bill_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bill_id'], ['bills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('campaign_id', 'bill_id')
    )

    # Legislators
    op.create_table('legislators',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bioguide_id', sa.String(20), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('party', sa.String(50), nullable=False),
        sa.Column('chamber', sa.String(20), nullable=False),
        sa.Column('state', sa.String(2), nullable=False),
        sa.Column('district', sa.String(10), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.Text(), nullable=True),
        sa.Column('office_address', sa.Text(), nullable=True),
        sa.Column('twitter_handle', sa.String(100), nullable=True),
        sa.Column('facebook_id', sa.String(100), nullable=True),
        sa.Column('stance', sa.String(50), nullable=False, server_default='unknown'),
        sa.Column('committees', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('leadership_positions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bioguide_id')
    )
    op.create_index('ix_legislators_full_name', 'legislators', ['full_name'])
    op.create_index('ix_legislators_party', 'legislators', ['party'])
    op.create_index('ix_legislators_chamber', 'legislators', ['chamber'])
    op.create_index('ix_legislators_state', 'legislators', ['state'])
    op.create_index('ix_legislators_bioguide_id', 'legislators', ['bioguide_id'])

    # Intelligence Items
    op.create_table('intelligence_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_name', sa.String(255), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('author', sa.String(255), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('entities', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('keywords', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('is_opposition', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_response', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='new'),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_intelligence_source_type', 'intelligence_items', ['source_type'])
    op.create_index('ix_intelligence_external_id', 'intelligence_items', ['external_id'])
    op.create_index('ix_intelligence_relevance', 'intelligence_items', ['relevance_score'])
    op.create_index('ix_intelligence_is_opposition', 'intelligence_items', ['is_opposition'])
    op.create_index('ix_intelligence_priority', 'intelligence_items', ['priority'])
    op.create_index('ix_intelligence_status', 'intelligence_items', ['status'])
    op.create_index('ix_intelligence_published_at', 'intelligence_items', ['published_at'])

    # Claims
    op.create_table('claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('source', sa.Text(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('source_author', sa.String(255), nullable=True),
        sa.Column('verification_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('verdict', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('evidence', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('rebuttal', sa.Text(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('checked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_claims_verification_status', 'claims', ['verification_status'])

    # Content Items
    op.create_table('content_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('hashtags', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('mentions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('media_urls', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('target_audience', sa.String(255), nullable=True),
        sa.Column('target_platform', sa.String(50), nullable=True),
        sa.Column('target_legislator_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('variant', sa.String(50), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['target_legislator_id'], ['legislators.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['content_items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_content_campaign_id', 'content_items', ['campaign_id'])
    op.create_index('ix_content_content_type', 'content_items', ['content_type'])
    op.create_index('ix_content_status', 'content_items', ['status'])

    # Actions
    op.create_table('actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('target_legislators', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('target_regions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('estimated_time_hours', sa.Float(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('volunteers_needed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('effort_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('assigned_to', sa.String(255), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_actions_campaign_id', 'actions', ['campaign_id'])
    op.create_index('ix_actions_action_type', 'actions', ['action_type'])
    op.create_index('ix_actions_priority', 'actions', ['priority'])
    op.create_index('ix_actions_status', 'actions', ['status'])

    # Metrics
    op.create_table('metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metric_type', sa.String(100), nullable=False),
        sa.Column('metric_name', sa.String(255), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('previous_value', sa.Float(), nullable=True),
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('dimensions', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('period_start', sa.DateTime(), nullable=True),
        sa.Column('period_end', sa.DateTime(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metrics_campaign_id', 'metrics', ['campaign_id'])
    op.create_index('ix_metrics_metric_type', 'metrics', ['metric_type'])
    op.create_index('ix_metrics_recorded_at', 'metrics', ['recorded_at'])

    # Supporters
    op.create_table('supporters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('state', sa.String(2), nullable=True),
        sa.Column('zip_code', sa.String(10), nullable=True),
        sa.Column('congressional_district', sa.String(10), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('actions_taken', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_action_at', sa.DateTime(), nullable=True),
        sa.Column('email_opted_in', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sms_opted_in', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_supporters_email', 'supporters', ['email'])
    op.create_index('ix_supporters_state', 'supporters', ['state'])
    op.create_index('ix_supporters_engagement_score', 'supporters', ['engagement_score'])

    # Agent Events (Audit Log)
    op.create_table('agent_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('input_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('output_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_events_agent_type', 'agent_events', ['agent_type'])
    op.create_index('ix_agent_events_event_type', 'agent_events', ['event_type'])
    op.create_index('ix_agent_events_created_at', 'agent_events', ['created_at'])


def downgrade() -> None:
    op.drop_table('agent_events')
    op.drop_table('supporters')
    op.drop_table('metrics')
    op.drop_table('actions')
    op.drop_table('content_items')
    op.drop_table('claims')
    op.drop_table('intelligence_items')
    op.drop_table('legislators')
    op.drop_table('campaign_bills')
    op.drop_table('bills')
    op.drop_table('campaigns')
