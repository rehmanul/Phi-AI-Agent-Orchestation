"""
Distribution & Outreach Agent

Delivers content to targets via email, social media, and other channels.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import select

from agents.base import BaseAgent
from core.config import settings
from core.database import ContentItem, Legislator, Supporter, get_async_session
from core.messaging import AgentMessage, Topics

logger = structlog.get_logger()


class DistributionAgent(BaseAgent):
    """
    Distribution & Outreach Agent - The Campaign Dispatcher.
    
    Responsibilities:
    - Send emails via SendGrid
    - Post to social media platforms
    - Manage patch-through calls via Twilio
    - Segment and target supporters
    - Schedule and time content delivery
    """
    
    AGENT_TYPE = "distribution"
    CONSUME_TOPICS = [Topics.DISTRIBUTION, Topics.COMMANDS]
    
    def _register_handlers(self) -> None:
        self.register_handler("urgent_content_ready", self._handle_urgent_content)
        self.register_handler("personalized_content_ready", self._handle_personalized)
        self.register_handler("send_email_campaign", self._handle_email_campaign)
        self.register_handler("post_social", self._handle_post_social)
        self.register_handler("schedule_content", self._handle_schedule)
    
    async def process(self, message: AgentMessage) -> None:
        handler = self._handlers.get(message.type)
        if handler:
            await handler(message)
    
    async def _handle_urgent_content(self, message: AgentMessage) -> None:
        """Distribute urgent content immediately."""
        content = message.payload
        
        # Post to social immediately
        if content.get("content_type") in ("rebuttal", "rapid_response", "tweets"):
            await self._post_to_social(content)
        
        # Also email key supporters
        await self._email_segment("active", content)
        
        # Log metrics
        await self._track_distribution(content, "urgent")
    
    async def _handle_personalized(self, message: AgentMessage) -> None:
        """Handle personalized content for specific legislator."""
        content = message.payload.get("content", {})
        legislator_id = message.payload.get("target_legislator")
        
        # Find supporters in that legislator's district
        supporters = await self._get_supporters_for_legislator(legislator_id)
        
        if supporters:
            await self._send_personalized_emails(content, supporters)
    
    async def _handle_email_campaign(self, message: AgentMessage) -> None:
        """Send an email campaign."""
        segment = message.payload.get("segment", "all")
        content = message.payload.get("content", {})
        subject = message.payload.get("subject", "Campaign Update")
        
        supporters = await self._get_supporters_by_segment(segment)
        
        for supporter in supporters:
            await self._send_email(
                to_email=supporter.email,
                to_name=f"{supporter.first_name} {supporter.last_name}",
                subject=subject,
                body=content.get("body", ""),
            )
        
        # Track metrics
        await self.send_message(
            Topics.FEEDBACK,
            AgentMessage(
                type="email_campaign_sent",
                source_agent=self.AGENT_TYPE,
                payload={
                    "segment": segment,
                    "recipients": len(supporters),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            ),
        )
    
    async def _handle_post_social(self, message: AgentMessage) -> None:
        """Post to social media."""
        platform = message.payload.get("platform", "twitter")
        content = message.payload.get("content", "")
        
        if platform == "twitter":
            await self._post_to_twitter(content)
        elif platform == "all":
            await self._post_to_all_platforms(content)
    
    async def _handle_schedule(self, message: AgentMessage) -> None:
        """Schedule content for future posting."""
        content = message.payload.get("content", {})
        schedule_time = message.payload.get("schedule_time")
        platforms = message.payload.get("platforms", ["twitter"])
        
        # Save to database with scheduled status
        async with get_async_session() as session:
            item = ContentItem(
                content_type=content.get("content_type", "social"),
                title=content.get("title"),
                body=content.get("body", ""),
                status="scheduled",
                target_platform=",".join(platforms),
                metadata={"schedule_time": schedule_time},
            )
            session.add(item)
            await session.commit()
        
        self.logger.info("Content scheduled", schedule_time=schedule_time)
    
    async def _post_to_social(self, content: Dict) -> None:
        """Post content to social media platforms."""
        body = content.get("body", "")
        
        # Extract tweets if multiple
        if "---" in body:
            tweets = body.split("---")
        else:
            tweets = [body[:280]]
        
        for tweet in tweets:
            tweet = tweet.strip()
            if tweet:
                await self._post_to_twitter(tweet)
    
    async def _post_to_twitter(self, text: str) -> None:
        """Post to Twitter/X."""
        try:
            from integrations.social import TwitterClient
            
            client = TwitterClient()
            tweet_id = await client.post_tweet(text)
            
            if tweet_id:
                self.logger.info("Posted to Twitter", tweet_id=tweet_id)
                
                await self.send_message(
                    Topics.FEEDBACK,
                    AgentMessage(
                        type="social_post",
                        source_agent=self.AGENT_TYPE,
                        payload={
                            "platform": "twitter",
                            "post_id": tweet_id,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    ),
                )
        except Exception as e:
            self.logger.error("Twitter post failed", error=str(e))
    
    async def _post_to_all_platforms(self, content: str) -> None:
        """Post to all configured platforms."""
        await self._post_to_twitter(content[:280])
        # Add Reddit, Facebook, etc. as needed
    
    async def _send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body: str,
    ) -> bool:
        """Send an email via SendGrid."""
        if not settings.sendgrid_api_key:
            self.logger.warning("SendGrid not configured, skipping email")
            return False
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=(settings.sendgrid_from_email, settings.sendgrid_from_name),
                to_emails=to_email,
                subject=subject,
                html_content=body,
            )
            
            sg = SendGridAPIClient(settings.sendgrid_api_key)
            response = sg.send(message)
            
            self.logger.info(
                "Email sent",
                to=to_email,
                status=response.status_code,
            )
            return response.status_code == 202
            
        except Exception as e:
            self.logger.error("Email send failed", error=str(e))
            return False
    
    async def _email_segment(self, segment: str, content: Dict) -> None:
        """Email a segment of supporters."""
        supporters = await self._get_supporters_by_segment(segment)
        
        for supporter in supporters[:100]:  # Limit batch
            await self._send_email(
                to_email=supporter.email,
                to_name=supporter.first_name or "Supporter",
                subject=content.get("title", "Urgent Update"),
                body=content.get("body", ""),
            )
    
    async def _get_supporters_by_segment(self, segment: str) -> List[Any]:
        """Get supporters by segment."""
        async with get_async_session() as session:
            if segment == "all":
                result = await session.execute(
                    select(Supporter).where(Supporter.email_opted_in == True)
                )
            elif segment == "active":
                result = await session.execute(
                    select(Supporter).where(
                        Supporter.email_opted_in == True,
                        Supporter.engagement_score >= 0.5,
                    )
                )
            else:
                result = await session.execute(
                    select(Supporter).where(
                        Supporter.email_opted_in == True,
                        Supporter.tags.contains([segment]),
                    )
                )
            return result.scalars().all()
    
    async def _get_supporters_for_legislator(self, legislator_id: str) -> List[Any]:
        """Get supporters in a legislator's district."""
        async with get_async_session() as session:
            # 1. Get the legislator to find their state/district
            stmt = select(Legislator).where(Legislator.id == legislator_id)
            result = await session.execute(stmt)
            legislator = result.scalar_one_or_none()

            if not legislator:
                self.logger.warning("Legislator not found", legislator_id=legislator_id)
                return []

            # 2. Find supporters in that district
            # Note: Legislator.district maps to Supporter.congressional_district
            stmt = select(Supporter).where(
                Supporter.state == legislator.state,
                Supporter.congressional_district == legislator.district,
                Supporter.email_opted_in == True
            )
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def _send_personalized_emails(
        self, content: Dict, supporters: List
    ) -> None:
        """Send personalized emails to supporters."""
        for supporter in supporters:
            personalized_body = content.get("body", "").replace(
                "[NAME]", supporter.first_name or "Friend"
            )
            await self._send_email(
                to_email=supporter.email,
                to_name=supporter.first_name or "",
                subject=content.get("title", "Action Needed"),
                body=personalized_body,
            )
    
    async def _track_distribution(self, content: Dict, dist_type: str) -> None:
        """Track distribution metrics."""
        await self.send_message(
            Topics.FEEDBACK,
            AgentMessage(
                type="distribution_complete",
                source_agent=self.AGENT_TYPE,
                payload={
                    "distribution_type": dist_type,
                    "content_type": content.get("content_type"),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            ),
        )


async def main():
    from agents.base import run_agent
    await run_agent(DistributionAgent())

if __name__ == "__main__":
    asyncio.run(main())
