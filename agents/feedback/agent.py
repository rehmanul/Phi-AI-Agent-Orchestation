"""
Feedback & Analytics Agent

Monitors campaign performance, tracks metrics, and provides insights
to optimize the advocacy campaign.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from agents.base import BaseAgent
from core.database import Action, ContentItem, Metric, get_async_session
from core.messaging import AgentMessage, Topics

logger = structlog.get_logger()


class CampaignMetrics(BaseModel):
    """Campaign performance metrics."""
    
    period: str
    total_content_created: int = 0
    content_published: int = 0
    emails_sent: int = 0
    social_posts: int = 0
    social_engagement: int = 0
    actions_completed: int = 0
    actions_pending: int = 0
    
    # Trends
    engagement_trend: str = "stable"  # up, down, stable
    recommendations: List[str] = Field(default_factory=list)


class FeedbackAgent(BaseAgent):
    """
    Feedback & Analytics Agent - The Campaign Analyst.
    
    Responsibilities:
    - Track all campaign metrics
    - Monitor content performance
    - A/B test messaging
    - Generate performance reports
    - Recommend optimizations
    """
    
    AGENT_TYPE = "feedback"
    CONSUME_TOPICS = [Topics.FEEDBACK, Topics.EVENTS, Topics.COMMANDS]
    
    def _register_handlers(self) -> None:
        self.register_handler("email_campaign_sent", self._handle_email_sent)
        self.register_handler("social_post", self._handle_social_post)
        self.register_handler("distribution_complete", self._handle_distribution)
        self.register_handler("generate_report", self._handle_generate_report)
        self.register_handler("track_metric", self._handle_track_metric)
    
    async def process(self, message: AgentMessage) -> None:
        handler = self._handlers.get(message.type)
        if handler:
            await handler(message)
    
    async def _handle_email_sent(self, message: AgentMessage) -> None:
        """Track email campaign metrics."""
        recipients = message.payload.get("recipients", 0)
        segment = message.payload.get("segment", "unknown")
        
        await self._record_metric(
            metric_type="email_sent",
            metric_name=f"Emails sent to {segment}",
            value=recipients,
        )
    
    async def _handle_social_post(self, message: AgentMessage) -> None:
        """Track social media post."""
        platform = message.payload.get("platform")
        post_id = message.payload.get("post_id")
        
        await self._record_metric(
            metric_type="social_post",
            metric_name=f"Post on {platform}",
            value=1,
            dimensions={"platform": platform, "post_id": post_id},
        )
    
    async def _handle_distribution(self, message: AgentMessage) -> None:
        """Track content distribution."""
        dist_type = message.payload.get("distribution_type")
        content_type = message.payload.get("content_type")
        
        await self._record_metric(
            metric_type="distribution",
            metric_name=f"{dist_type} {content_type}",
            value=1,
        )
    
    async def _handle_generate_report(self, message: AgentMessage) -> None:
        """Generate a campaign performance report."""
        period_hours = message.payload.get("period_hours", 24)
        campaign_id = message.payload.get("campaign_id")
        
        report = await self._generate_performance_report(campaign_id, period_hours)
        
        # Send report to strategy agent for planning
        await self.send_message(
            Topics.STRATEGY,
            AgentMessage(
                type="performance_report",
                source_agent=self.AGENT_TYPE,
                payload=report.model_dump(),
            ),
        )
    
    async def _handle_track_metric(self, message: AgentMessage) -> None:
        """Track a custom metric."""
        await self._record_metric(
            metric_type=message.payload.get("type", "custom"),
            metric_name=message.payload.get("name", "Custom Metric"),
            value=message.payload.get("value", 0),
            dimensions=message.payload.get("dimensions"),
        )
    
    async def _record_metric(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        campaign_id: Optional[str] = None,
        dimensions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a metric to the database."""
        async with get_async_session() as session:
            metric = Metric(
                campaign_id=campaign_id if campaign_id else None,
                metric_type=metric_type,
                metric_name=metric_name,
                value=value,
                dimensions=dimensions or {},
                recorded_at=datetime.utcnow(),
            )
            session.add(metric)
            await session.commit()
        
        self.logger.debug(
            "Metric recorded",
            type=metric_type,
            name=metric_name,
            value=value,
        )
    
    async def _generate_performance_report(
        self, campaign_id: Optional[str], period_hours: int
    ) -> CampaignMetrics:
        """Generate a comprehensive performance report."""
        since = datetime.utcnow() - timedelta(hours=period_hours)
        
        async with get_async_session() as session:
            # Count content items
            content_result = await session.execute(
                select(func.count(ContentItem.id)).where(
                    ContentItem.created_at >= since
                )
            )
            total_content = content_result.scalar() or 0
            
            published_result = await session.execute(
                select(func.count(ContentItem.id)).where(
                    ContentItem.created_at >= since,
                    ContentItem.status == "published",
                )
            )
            published_content = published_result.scalar() or 0
            
            # Count actions
            actions_result = await session.execute(
                select(func.count(Action.id)).where(
                    Action.created_at >= since,
                    Action.status == "completed",
                )
            )
            completed_actions = actions_result.scalar() or 0
            
            pending_result = await session.execute(
                select(func.count(Action.id)).where(
                    Action.status == "pending",
                )
            )
            pending_actions = pending_result.scalar() or 0
            
            # Aggregate metrics
            email_result = await session.execute(
                select(func.sum(Metric.value)).where(
                    Metric.recorded_at >= since,
                    Metric.metric_type == "email_sent",
                )
            )
            emails_sent = int(email_result.scalar() or 0)
            
            social_result = await session.execute(
                select(func.count(Metric.id)).where(
                    Metric.recorded_at >= since,
                    Metric.metric_type == "social_post",
                )
            )
            social_posts = social_result.scalar() or 0
        
        # Generate recommendations
        recommendations = await self._generate_recommendations({
            "content_created": total_content,
            "content_published": published_content,
            "emails_sent": emails_sent,
            "social_posts": social_posts,
            "actions_completed": completed_actions,
            "actions_pending": pending_actions,
        })
        
        return CampaignMetrics(
            period=f"Last {period_hours} hours",
            total_content_created=total_content,
            content_published=published_content,
            emails_sent=emails_sent,
            social_posts=social_posts,
            actions_completed=completed_actions,
            actions_pending=pending_actions,
            recommendations=recommendations,
        )
    
    async def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []
        
        # Content velocity
        if metrics.get("content_created", 0) > 0:
            publish_rate = metrics.get("content_published", 0) / metrics["content_created"]
            if publish_rate < 0.5:
                recommendations.append(
                    "Low content publish rate. Review and approve pending content."
                )
        
        # Action completion
        pending = metrics.get("actions_pending", 0)
        if pending > 10:
            recommendations.append(
                f"{pending} actions pending. Prioritize high-impact items."
            )
        
        # Social activity
        if metrics.get("social_posts", 0) < 3:
            recommendations.append(
                "Low social media activity. Consider increasing posting frequency."
            )
        
        # Email engagement
        if metrics.get("emails_sent", 0) == 0:
            recommendations.append(
                "No emails sent this period. Engage supporters with updates."
            )
        
        if not recommendations:
            recommendations.append("Campaign metrics look healthy. Maintain current pace.")
        
        return recommendations
    
    async def _periodic_task(self) -> None:
        """Generate periodic reports."""
        # Generate daily report at midnight
        now = datetime.utcnow()
        if now.hour == 0 and now.minute < 5:
            report = await self._generate_performance_report(None, 24)
            
            await self.send_message(
                Topics.STRATEGY,
                AgentMessage(
                    type="daily_report",
                    source_agent=self.AGENT_TYPE,
                    payload=report.model_dump(),
                ),
            )


async def main():
    from agents.base import run_agent
    await run_agent(FeedbackAgent())

if __name__ == "__main__":
    asyncio.run(main())
