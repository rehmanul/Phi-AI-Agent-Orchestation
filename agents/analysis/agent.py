"""
Analysis & Fact-Checking Agent

Processes intelligence items, summarizes information, verifies claims,
and generates daily intelligence briefs.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field
from sqlalchemy import select, and_

from agents.base import BaseAgent
from core.config import settings
from core.database import Claim, IntelligenceItem, get_async_session
from core.llm import get_llm_client
from core.messaging import AgentMessage, Topics

logger = structlog.get_logger()


# =============================================================================
# Analysis Output Models
# =============================================================================

class IntelligenceSummary(BaseModel):
    """Summary of intelligence items."""
    
    period: str
    total_items: int
    by_source: Dict[str, int]
    key_developments: List[str]
    opposition_activity: List[str]
    recommended_actions: List[str]


class ClaimVerification(BaseModel):
    """Result of fact-checking a claim."""
    
    claim: str
    verdict: str  # true, false, misleading, unverified, needs_context
    confidence: float
    evidence: List[str]
    rebuttal: Optional[str] = None
    sources: List[str] = Field(default_factory=list)


class EntityExtraction(BaseModel):
    """Extracted entities from text."""
    
    people: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    bills: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)


# =============================================================================
# Analysis Agent
# =============================================================================

class AnalysisAgent(BaseAgent):
    """
    Analysis & Fact-Checking Agent.
    
    Responsibilities:
    - Analyze and summarize intelligence items
    - Extract entities and keywords
    - Verify claims against trusted sources
    - Detect opposition talking points
    - Generate daily intelligence briefs
    
    Input:
    - Intelligence items from INTELLIGENCE topic
    - Analysis requests from other agents
    
    Output:
    - Enriched intelligence to ANALYSIS topic
    - Verified claims to database
    - Briefs to STRATEGY topic
    """
    
    AGENT_TYPE = "analysis"
    CONSUME_TOPICS = [Topics.INTELLIGENCE, Topics.COMMANDS]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Known opposition claims to watch for
        self.opposition_patterns = [
            "radiation",
            "health hazard",
            "unsafe",
            "dangerous",
            "cancer",
            "electromagnetic",
            "untested",
            "expensive",
            "doesn't work",
            "scam",
        ]
        
        # Trusted sources for fact-checking
        self.trusted_sources = [
            "fcc.gov",
            "ieee.org",
            "cdc.gov",
            "fda.gov",
            "congress.gov",
            "doi.org",
            "nih.gov",
        ]
    
    def _register_handlers(self) -> None:
        """Register message handlers."""
        self.register_handler("intelligence_item", self._handle_intelligence_item)
        self.register_handler("analysis_request", self._handle_analysis_request)
        self.register_handler("fact_check_request", self._handle_fact_check_request)
        self.register_handler("generate_brief", self._handle_generate_brief)
    
    async def process(self, message: AgentMessage) -> None:
        """Process incoming messages."""
        handler = self._handlers.get(message.type)
        if handler:
            await handler(message)
        else:
            self.logger.warning("No handler for message type", type=message.type)
    
    # =========================================================================
    # Message Handlers
    # =========================================================================
    
    async def _handle_intelligence_item(self, message: AgentMessage) -> None:
        """Analyze an incoming intelligence item."""
        item_id = message.payload.get("item_id")
        item_type = message.payload.get("type")
        
        self.logger.debug("Analyzing intelligence item", item_id=item_id, type=item_type)
        
        # Load item from database
        async with get_async_session() as session:
            result = await session.execute(
                select(IntelligenceItem).where(IntelligenceItem.id == item_id)
            )
            item = result.scalar()
            
            if not item:
                self.logger.warning("Intelligence item not found", item_id=item_id)
                return
            
            # Analyze content
            analysis = await self._analyze_content(item.content or item.title or "")
            
            # Update item with analysis
            item.summary = analysis.get("summary", item.summary)
            item.relevance_score = analysis.get("relevance_score", item.relevance_score)
            item.sentiment_score = analysis.get("sentiment_score")
            item.entities = analysis.get("entities", [])
            item.is_opposition = analysis.get("is_opposition", item.is_opposition)
            item.status = "reviewed"
            
            await session.commit()
            
            # Check for claims that need verification
            if analysis.get("claims"):
                for claim_text in analysis["claims"]:
                    await self._queue_claim_verification(claim_text, item.source_url)
            
            # Emit analyzed intelligence
            await self.send_message(
                Topics.ANALYSIS,
                AgentMessage(
                    type="intelligence_analyzed",
                    source_agent=self.AGENT_TYPE,
                    payload={
                        "item_id": str(item.id),
                        "summary": item.summary,
                        "relevance_score": item.relevance_score,
                        "is_opposition": item.is_opposition,
                        "entities": item.entities,
                    },
                ),
            )
    
    async def _handle_analysis_request(self, message: AgentMessage) -> None:
        """Handle an ad-hoc analysis request."""
        text = message.payload.get("text", "")
        analysis_type = message.payload.get("analysis_type", "full")
        
        if analysis_type == "summary":
            summary = await self.llm.summarize(text)
            result = {"summary": summary}
        elif analysis_type == "entities":
            entities = await self.llm.extract_entities(text)
            result = {"entities": entities}
        elif analysis_type == "sentiment":
            sentiment = await self.llm.analyze_sentiment(text)
            result = {"sentiment": sentiment}
        else:
            result = await self._analyze_content(text)
        
        # Send response
        await self.send_message(
            Topics.ANALYSIS,
            AgentMessage(
                type="analysis_response",
                source_agent=self.AGENT_TYPE,
                target_agent=message.source_agent,
                correlation_id=message.correlation_id,
                payload=result,
            ),
        )
    
    async def _handle_fact_check_request(self, message: AgentMessage) -> None:
        """Fact-check a specific claim."""
        claim_text = message.payload.get("claim", "")
        source = message.payload.get("source")
        
        verification = await self._verify_claim(claim_text, source)
        
        # Store in database
        async with get_async_session() as session:
            claim = Claim(
                claim_text=claim_text,
                source=source,
                verification_status=verification.verdict,
                verdict=verification.verdict,
                confidence_score=verification.confidence,
                evidence=[{"text": e} for e in verification.evidence],
                rebuttal=verification.rebuttal,
            )
            session.add(claim)
            await session.commit()
        
        # Send response
        await self.send_message(
            Topics.ANALYSIS,
            AgentMessage(
                type="fact_check_response",
                source_agent=self.AGENT_TYPE,
                target_agent=message.source_agent,
                correlation_id=message.correlation_id,
                payload=verification.model_dump(),
            ),
        )
    
    async def _handle_generate_brief(self, message: AgentMessage) -> None:
        """Generate a daily intelligence brief."""
        period_hours = message.payload.get("period_hours", 24)
        
        brief = await self._generate_intelligence_brief(period_hours)
        
        # Send to strategy agent
        await self.send_message(
            Topics.STRATEGY,
            AgentMessage(
                type="intelligence_brief",
                source_agent=self.AGENT_TYPE,
                target_agent="strategy",
                payload=brief.model_dump(),
            ),
        )
    
    # =========================================================================
    # Analysis Methods
    # =========================================================================
    
    async def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive analysis on text content."""
        if not text or len(text) < 10:
            return {"summary": text, "relevance_score": 0.0}
        
        # Use LLM for analysis
        system_prompt = """
You are an expert political analyst specializing in technology policy.
Analyze the provided text and extract:
1. A concise summary (2-3 sentences)
2. Relevance score (0-1) for wireless power/charging policy
3. Sentiment score (-1 to 1, negative to positive toward wireless power)
4. Whether this appears to be opposition content (true/false)
5. Key entities mentioned (people, organizations, bills)
6. Any factual claims that should be verified

Respond in JSON format.
"""
        
        prompt = f"""Analyze this text:

{text[:3000]}

Provide analysis in this JSON structure:
{{
    "summary": "...",
    "relevance_score": 0.0-1.0,
    "sentiment_score": -1.0 to 1.0,
    "is_opposition": true/false,
    "entities": ["person1", "org1", ...],
    "claims": ["claim1", "claim2", ...]
}}
"""
        
        try:
            response = await self.llm.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON from response
            import json
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                analysis = json.loads(response[start:end])
                return analysis
            
            return {"summary": text[:200], "relevance_score": 0.5}
            
        except Exception as e:
            self.logger.warning("Analysis failed", error=str(e))
            return {"summary": text[:200], "relevance_score": 0.5}
    
    async def _verify_claim(self, claim: str, source: Optional[str] = None) -> ClaimVerification:
        """Verify a factual claim using LLM and trusted sources."""
        system_prompt = """
You are a fact-checker specializing in technology and policy claims.
Evaluate claims about wireless power, wireless charging, and related technologies.
Be objective and cite specific evidence.
"""
        
        prompt = f"""
Fact-check this claim: "{claim}"

Source: {source or "Unknown"}

Evaluate whether this claim is:
- TRUE: Supported by evidence
- FALSE: Contradicted by evidence  
- MISLEADING: Contains truth but is presented deceptively
- NEEDS_CONTEXT: Requires additional context to evaluate
- UNVERIFIED: Cannot be confirmed or denied

Provide:
1. Your verdict
2. Confidence score (0-1)
3. Evidence supporting your verdict
4. If false/misleading, a rebuttal statement
5. Trusted sources if available

Respond in JSON format:
{{
    "verdict": "true|false|misleading|needs_context|unverified",
    "confidence": 0.0-1.0,
    "evidence": ["point1", "point2"],
    "rebuttal": "...",
    "sources": ["source1", "source2"]
}}
"""
        
        try:
            response = await self.llm.generate(prompt, system_prompt=system_prompt)
            
            import json
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                return ClaimVerification(
                    claim=claim,
                    verdict=data.get("verdict", "unverified"),
                    confidence=data.get("confidence", 0.5),
                    evidence=data.get("evidence", []),
                    rebuttal=data.get("rebuttal"),
                    sources=data.get("sources", []),
                )
            
            return ClaimVerification(
                claim=claim,
                verdict="unverified",
                confidence=0.3,
                evidence=["Unable to verify automatically"],
            )
            
        except Exception as e:
            self.logger.warning("Claim verification failed", error=str(e))
            return ClaimVerification(
                claim=claim,
                verdict="unverified",
                confidence=0.0,
                evidence=[f"Verification error: {str(e)}"],
            )
    
    async def _queue_claim_verification(self, claim: str, source: Optional[str]) -> None:
        """Queue a claim for verification."""
        # Check if already verified
        async with get_async_session() as session:
            existing = await session.execute(
                select(Claim).where(Claim.claim_text == claim)
            )
            if existing.scalar():
                return
        
        # Queue for verification (could be async job in production)
        verification = await self._verify_claim(claim, source)
        
        async with get_async_session() as session:
            claim_record = Claim(
                claim_text=claim,
                source=source,
                verification_status=verification.verdict,
                verdict=verification.verdict,
                confidence_score=verification.confidence,
                evidence=[{"text": e} for e in verification.evidence],
                rebuttal=verification.rebuttal,
                checked_at=datetime.utcnow(),
            )
            session.add(claim_record)
            await session.commit()
    
    async def _generate_intelligence_brief(self, period_hours: int = 24) -> IntelligenceSummary:
        """Generate a summary brief of recent intelligence."""
        since = datetime.utcnow() - timedelta(hours=period_hours)
        
        async with get_async_session() as session:
            # Get recent items
            result = await session.execute(
                select(IntelligenceItem).where(
                    IntelligenceItem.created_at >= since
                ).order_by(IntelligenceItem.relevance_score.desc())
            )
            items = result.scalars().all()
            
            # Aggregate by source
            by_source: Dict[str, int] = {}
            opposition_items = []
            high_relevance = []
            
            for item in items:
                by_source[item.source_type] = by_source.get(item.source_type, 0) + 1
                
                if item.is_opposition:
                    opposition_items.append(item)
                
                if item.relevance_score >= 0.7:
                    high_relevance.append(item)
            
            # Generate summary using LLM
            if high_relevance:
                items_text = "\n".join([
                    f"- [{i.source_type}] {i.title or i.content[:100]}"
                    for i in high_relevance[:10]
                ])
                
                summary_prompt = f"""
Based on these recent developments in wireless power policy:

{items_text}

Provide:
1. 3-5 key developments (one sentence each)
2. Summary of any opposition activity
3. 2-3 recommended actions for the advocacy campaign

Format as JSON:
{{
    "key_developments": ["...", "..."],
    "opposition_summary": ["...", "..."],
    "recommended_actions": ["...", "..."]
}}
"""
                
                try:
                    response = await self.llm.generate(summary_prompt)
                    import json
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(response[start:end])
                        return IntelligenceSummary(
                            period=f"Last {period_hours} hours",
                            total_items=len(items),
                            by_source=by_source,
                            key_developments=data.get("key_developments", []),
                            opposition_activity=data.get("opposition_summary", []),
                            recommended_actions=data.get("recommended_actions", []),
                        )
                except Exception as e:
                    self.logger.warning("Brief generation failed", error=str(e))
            
            return IntelligenceSummary(
                period=f"Last {period_hours} hours",
                total_items=len(items),
                by_source=by_source,
                key_developments=[],
                opposition_activity=[],
                recommended_actions=[],
            )


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Run the analysis agent."""
    from agents.base import run_agent
    
    agent = AnalysisAgent()
    await run_agent(agent)


if __name__ == "__main__":
    asyncio.run(main())
