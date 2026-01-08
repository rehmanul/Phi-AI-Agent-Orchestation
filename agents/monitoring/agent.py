"""
Monitoring Agent

Continuously scans legislative, news, social media, and regulatory sources
for relevant information. This is the "eyes and ears" of the advocacy system.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog
from sqlalchemy import select

from agents.base import AgentState, BaseAgent
from core.config import settings
from core.database import IntelligenceItem, get_async_session
from core.messaging import AgentMessage, Topics

logger = structlog.get_logger()


class MonitoringAgent(BaseAgent):
    """
    Monitoring Agent - The "Eyes and Ears" of the advocacy system.
    
    Responsibilities:
    - Monitor legislative updates (Congress.gov, state legislatures)
    - Track news coverage (NewsAPI, Google News)
    - Monitor social media (Twitter, Reddit)
    - Detect regulatory filings
    - Generate real-time alerts for significant developments
    
    Output:
    - Intelligence items published to Kafka INTELLIGENCE topic
    - Alerts for high-priority items to ALERTS topic
    """
    
    AGENT_TYPE = "monitoring"
    CONSUME_TOPICS = [Topics.COMMANDS]  # Listen for commands to trigger scans
    
    def __init__(
        self,
        campaign_keywords: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        
        # Default keywords for wireless power advocacy
        self.keywords = campaign_keywords or [
            "wireless power",
            "wireless charging",
            "inductive charging",
            "power over air",
            "Wi-Charge",
            "wireless energy transfer",
            "long range wireless power",
            "radio frequency power",
        ]
        
        # Monitored bills (loaded from database on start)
        self.tracked_bills: List[Dict[str, Any]] = []
        
        # Rate limiting state
        self._last_legislative_scan: Optional[datetime] = None
        self._last_news_scan: Optional[datetime] = None
        self._last_social_scan: Optional[datetime] = None
        
        # Scan intervals (from settings)
        self._legislative_interval = settings.monitoring_legislative_interval
        self._news_interval = settings.monitoring_news_interval
        self._social_interval = settings.monitoring_social_interval
    
    def _register_handlers(self) -> None:
        """Register message handlers."""
        self.register_handler("scan_command", self._handle_scan_command)
        self.register_handler("add_keyword", self._handle_add_keyword)
        self.register_handler("track_bill", self._handle_track_bill)
    
    async def _on_start(self) -> None:
        """Initialize monitoring resources on startup."""
        self.logger.info("Initializing monitoring agent")
        
        # Load tracked bills from database
        await self._load_tracked_bills()
        
        # Start background scanning tasks
        asyncio.create_task(self._legislative_scan_loop())
        asyncio.create_task(self._news_scan_loop())
        asyncio.create_task(self._social_scan_loop())
        
        self.logger.info(
            "Monitoring agent ready",
            keywords=len(self.keywords),
            tracked_bills=len(self.tracked_bills),
        )
    
    async def process(self, message: AgentMessage) -> None:
        """Process incoming messages."""
        # Dispatch to registered handlers
        handler = self._handlers.get(message.type)
        if handler:
            await handler(message)
        else:
            self.logger.warning("No handler for message type", type=message.type)
    
    # =========================================================================
    # Message Handlers
    # =========================================================================
    
    async def _handle_scan_command(self, message: AgentMessage) -> None:
        """Handle manual scan trigger."""
        scan_type = message.payload.get("scan_type", "all")
        
        self.logger.info("Manual scan triggered", scan_type=scan_type)
        
        if scan_type in ("all", "legislative"):
            await self._scan_legislative()
        if scan_type in ("all", "news"):
            await self._scan_news()
        if scan_type in ("all", "social"):
            await self._scan_social()
    
    async def _handle_add_keyword(self, message: AgentMessage) -> None:
        """Add a new monitoring keyword."""
        keyword = message.payload.get("keyword")
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.logger.info("Added monitoring keyword", keyword=keyword)
    
    async def _handle_track_bill(self, message: AgentMessage) -> None:
        """Start tracking a specific bill."""
        bill_info = message.payload
        self.tracked_bills.append(bill_info)
        self.logger.info(
            "Now tracking bill",
            bill=bill_info.get("number"),
            congress=bill_info.get("congress"),
        )
    
    # =========================================================================
    # Scanning Loops
    # =========================================================================
    
    async def _legislative_scan_loop(self) -> None:
        """Background loop for legislative scanning."""
        while self._running:
            try:
                now = datetime.utcnow()
                
                if (
                    self._last_legislative_scan is None or
                    (now - self._last_legislative_scan).total_seconds() >= self._legislative_interval
                ):
                    await self._scan_legislative()
                    self._last_legislative_scan = now
                
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Legislative scan loop error", error=str(e))
                await asyncio.sleep(300)  # Wait 5 min on error
    
    async def _news_scan_loop(self) -> None:
        """Background loop for news scanning."""
        while self._running:
            try:
                now = datetime.utcnow()
                
                if (
                    self._last_news_scan is None or
                    (now - self._last_news_scan).total_seconds() >= self._news_interval
                ):
                    await self._scan_news()
                    self._last_news_scan = now
                
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("News scan loop error", error=str(e))
                await asyncio.sleep(300)
    
    async def _social_scan_loop(self) -> None:
        """Background loop for social media scanning."""
        while self._running:
            try:
                now = datetime.utcnow()
                
                if (
                    self._last_social_scan is None or
                    (now - self._last_social_scan).total_seconds() >= self._social_interval
                ):
                    await self._scan_social()
                    self._last_social_scan = now
                
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Social scan loop error", error=str(e))
                await asyncio.sleep(300)
    
    # =========================================================================
    # Scanning Methods
    # =========================================================================
    
    async def _scan_legislative(self) -> None:
        """Scan for legislative updates."""
        self.logger.info("Starting legislative scan")
        
        try:
            from integrations.congress import CongressAPIClient, get_current_congress
            
            async with CongressAPIClient() as client:
                # 1. Search for new bills matching keywords
                for keyword in self.keywords[:5]:  # Limit to prevent rate limiting
                    try:
                        bills = await client.search_bills_by_keyword(
                            [keyword],
                            congress=await get_current_congress(),
                            limit=20,
                        )
                        
                        for bill in bills:
                            await self._process_bill_intelligence(bill)
                        
                    except Exception as e:
                        self.logger.warning(
                            "Keyword search failed",
                            keyword=keyword,
                            error=str(e),
                        )
                
                # 2. Check status of tracked bills
                for tracked in self.tracked_bills:
                    try:
                        bill = await client.get_bill(
                            congress=tracked["congress"],
                            bill_type=tracked["bill_type"],
                            bill_number=tracked["bill_number"],
                        )
                        
                        # Check if status changed
                        if bill.latest_action_text != tracked.get("last_action"):
                            await self._emit_bill_update_alert(bill, tracked)
                            tracked["last_action"] = bill.latest_action_text
                        
                    except Exception as e:
                        self.logger.warning(
                            "Bill status check failed",
                            bill=tracked.get("number"),
                            error=str(e),
                        )
            
            self.logger.info("Legislative scan complete")
            
        except ImportError:
            self.logger.warning("Congress integration not available")
        except Exception as e:
            self.logger.error("Legislative scan failed", error=str(e))
    
    async def _scan_news(self) -> None:
        """Scan news sources."""
        self.logger.info("Starting news scan")
        
        try:
            from integrations.news import NewsAggregator
            
            from_date = datetime.utcnow() - timedelta(days=1)
            
            async with NewsAggregator() as aggregator:
                articles = await aggregator.search_advocacy_keywords(
                    self.keywords,
                    from_date=from_date,
                )
                
                self.logger.info("Found news articles", count=len(articles))
                
                for article in articles:
                    await self._process_news_intelligence(article)
            
            self.logger.info("News scan complete")
            
        except ImportError:
            self.logger.warning("News integration not available")
        except Exception as e:
            self.logger.error("News scan failed", error=str(e))
    
    async def _scan_social(self) -> None:
        """Scan social media."""
        self.logger.info("Starting social media scan")
        
        try:
            from integrations.social import SocialMediaMonitor
            
            monitor = SocialMediaMonitor()
            posts = await monitor.search_advocacy_keywords(self.keywords)
            
            self.logger.info("Found social posts", count=len(posts))
            
            for post in posts:
                await self._process_social_intelligence(post)
            
            self.logger.info("Social scan complete")
            
        except ImportError:
            self.logger.warning("Social integration not available")
        except Exception as e:
            self.logger.error("Social scan failed", error=str(e))
    
    # =========================================================================
    # Intelligence Processing
    # =========================================================================
    
    async def _process_bill_intelligence(self, bill) -> None:
        """Process a bill into intelligence item and emit."""
        # Check if we've already processed this
        async with get_async_session() as session:
            existing = await session.execute(
                select(IntelligenceItem).where(
                    IntelligenceItem.source_type == "legislative",
                    IntelligenceItem.external_id == f"bill_{bill.congress}_{bill.bill_type}_{bill.bill_number}",
                )
            )
            if existing.scalar():
                return  # Already processed
            
            # Create intelligence item
            item = IntelligenceItem(
                source_type="legislative",
                source_name="Congress.gov",
                source_url=bill.url,
                external_id=f"bill_{bill.congress}_{bill.bill_type}_{bill.bill_number}",
                title=bill.title,
                content=f"{bill.title}\n\nLatest Action: {bill.latest_action_text}",
                summary=f"{bill.bill_type.upper()}{bill.bill_number}: {bill.title[:200]}",
                relevance_score=0.8,  # Will be refined by analysis agent
                keywords=self.keywords,
                published_at=datetime.fromisoformat(bill.introduced_date) if bill.introduced_date else None,
                metadata={
                    "congress": bill.congress,
                    "bill_type": bill.bill_type,
                    "bill_number": bill.bill_number,
                    "policy_area": bill.policy_area,
                },
            )
            session.add(item)
            await session.commit()
            
            # Emit to Kafka
            await self.emit_intelligence({
                "type": "legislative",
                "item_id": str(item.id),
                "title": item.title,
                "url": item.source_url,
                "bill_info": {
                    "congress": bill.congress,
                    "bill_type": bill.bill_type,
                    "bill_number": bill.bill_number,
                },
            })
    
    async def _process_news_intelligence(self, article) -> None:
        """Process a news article into intelligence item."""
        async with get_async_session() as session:
            # Check for duplicates
            existing = await session.execute(
                select(IntelligenceItem).where(
                    IntelligenceItem.source_type == "news",
                    IntelligenceItem.source_url == article.url,
                )
            )
            if existing.scalar():
                return
            
            # Calculate rough relevance based on keyword matches
            title_lower = article.title.lower()
            matches = sum(1 for kw in self.keywords if kw.lower() in title_lower)
            relevance = min(1.0, 0.3 + (matches * 0.2))
            
            item = IntelligenceItem(
                source_type="news",
                source_name=article.source,
                source_url=article.url,
                external_id=f"news_{hash(article.url)}",
                title=article.title,
                content=article.description or "",
                summary=article.description[:500] if article.description else article.title,
                author=article.author,
                relevance_score=relevance,
                keywords=self.keywords,
                published_at=article.published_at,
            )
            session.add(item)
            await session.commit()
            
            await self.emit_intelligence({
                "type": "news",
                "item_id": str(item.id),
                "title": item.title,
                "source": item.source_name,
                "url": item.source_url,
            })
            
            # High-relevance alert
            if relevance >= 0.7:
                await self.emit_alert(
                    "high_relevance_news",
                    f"High-relevance news: {article.title}",
                    {"url": article.url, "source": article.source},
                    priority=7,
                )
    
    async def _process_social_intelligence(self, post) -> None:
        """Process a social media post into intelligence item."""
        async with get_async_session() as session:
            external_id = f"{post.platform}_{post.post_id}"
            
            existing = await session.execute(
                select(IntelligenceItem).where(
                    IntelligenceItem.source_type == post.platform,
                    IntelligenceItem.external_id == external_id,
                )
            )
            if existing.scalar():
                return
            
            # Calculate relevance and detect if opposition
            content_lower = post.content.lower()
            is_opposition = any(
                term in content_lower
                for term in ["dangerous", "unsafe", "radiation", "health risk", "scam"]
            )
            
            # Engagement score
            engagement = post.likes + post.shares + post.comments
            relevance = min(1.0, 0.3 + (engagement / 1000))
            
            item = IntelligenceItem(
                source_type=post.platform,
                source_name=post.platform.title(),
                source_url=post.url,
                external_id=external_id,
                title=post.content[:100] + "..." if len(post.content) > 100 else post.content,
                content=post.content,
                author=post.author,
                relevance_score=relevance,
                is_opposition=is_opposition,
                requires_response=is_opposition and engagement > 100,
                priority=8 if is_opposition and engagement > 100 else 3,
                published_at=post.created_at,
                metadata={
                    "likes": post.likes,
                    "shares": post.shares,
                    "comments": post.comments,
                    "hashtags": post.hashtags,
                },
            )
            session.add(item)
            await session.commit()
            
            await self.emit_intelligence({
                "type": "social",
                "platform": post.platform,
                "item_id": str(item.id),
                "author": post.author,
                "is_opposition": is_opposition,
                "engagement": engagement,
            })
            
            # Alert for opposition content needing response
            if item.requires_response:
                await self.emit_alert(
                    "opposition_content",
                    f"Opposition content detected on {post.platform} (engagement: {engagement})",
                    {"url": post.url, "author": post.author, "content": post.content[:200]},
                    priority=8,
                )
    
    async def _emit_bill_update_alert(self, bill, tracked: Dict) -> None:
        """Emit an alert for a bill status change."""
        await self.emit_alert(
            "bill_status_change",
            f"Bill status changed: {bill.bill_type.upper()}{bill.bill_number}",
            {
                "congress": bill.congress,
                "bill_type": bill.bill_type,
                "bill_number": bill.bill_number,
                "title": bill.title,
                "previous_action": tracked.get("last_action"),
                "new_action": bill.latest_action_text,
                "action_date": bill.latest_action_date,
            },
            priority=9,
        )
    
    # =========================================================================
    # Database Operations
    # =========================================================================
    
    async def _load_tracked_bills(self) -> None:
        """Load tracked bills from database."""
        # TODO: Load from campaigns table
        # For now, use empty list
        self.tracked_bills = []


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Run the monitoring agent."""
    from agents.base import run_agent
    
    agent = MonitoringAgent()
    await run_agent(agent)


if __name__ == "__main__":
    asyncio.run(main())
