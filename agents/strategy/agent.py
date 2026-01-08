"""
Strategy Planner Agent

High-level campaign planning, stakeholder analysis, and legislative navigation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from pydantic import BaseModel, Field
from sqlalchemy import select

from agents.base import BaseAgent
from core.database import Campaign, Legislator, get_async_session
from core.messaging import AgentMessage, Topics

logger = structlog.get_logger()


class StrategyAgent(BaseAgent):
    """
    Strategy Planner Agent - The Campaign Strategist.
    
    Responsibilities:
    - Stakeholder mapping and power dynamics analysis
    - Policy window detection
    - Coalition building recommendations
    - Legislator profiling and targeting
    - Campaign timeline planning
    
    Input:
    - Intelligence briefs from ANALYSIS topic
    - Campaign goals and constraints
    
    Output:
    - Strategic plans to TACTICS topic
    - Targeting recommendations
    - Timeline updates
    """
    
    AGENT_TYPE = "strategy"
    CONSUME_TOPICS = [Topics.STRATEGY, Topics.ANALYSIS, Topics.COMMANDS]
    
    def _register_handlers(self) -> None:
        self.register_handler("intelligence_brief", self._handle_intelligence_brief)
        self.register_handler("update_strategy", self._handle_update_strategy)
        self.register_handler("analyze_stakeholders", self._handle_analyze_stakeholders)
        self.register_handler("recommend_targets", self._handle_recommend_targets)
    
    async def process(self, message: AgentMessage) -> None:
        handler = self._handlers.get(message.type)
        if handler:
            await handler(message)
    
    async def _handle_intelligence_brief(self, message: AgentMessage) -> None:
        """Process intelligence brief and update strategy."""
        brief = message.payload
        
        # Analyze if strategy adjustments needed
        if brief.get("opposition_activity"):
            await self._generate_counter_strategy(brief["opposition_activity"])
        
        if brief.get("key_developments"):
            await self._check_policy_windows(brief["key_developments"])
    
    async def _handle_update_strategy(self, message: AgentMessage) -> None:
        """Update campaign strategy based on new information."""
        campaign_id = message.payload.get("campaign_id")
        new_info = message.payload.get("new_information")
        
        strategy_update = await self._generate_strategy_update(campaign_id, new_info)
        
        await self.send_message(
            Topics.TACTICS,
            AgentMessage(
                type="strategy_update",
                source_agent=self.AGENT_TYPE,
                target_agent="tactics",
                payload=strategy_update,
            ),
        )
    
    async def _handle_analyze_stakeholders(self, message: AgentMessage) -> None:
        """Analyze stakeholders for a campaign."""
        campaign_id = message.payload.get("campaign_id")
        
        analysis = await self._perform_stakeholder_analysis(campaign_id)
        
        await self.send_message(
            Topics.STRATEGY,
            AgentMessage(
                type="stakeholder_analysis",
                source_agent=self.AGENT_TYPE,
                correlation_id=message.correlation_id,
                payload=analysis,
            ),
        )
    
    async def _handle_recommend_targets(self, message: AgentMessage) -> None:
        """Recommend legislators to target."""
        campaign_id = message.payload.get("campaign_id")
        action_type = message.payload.get("action_type", "general")
        
        recommendations = await self._generate_targeting_recommendations(
            campaign_id, action_type
        )
        
        await self.send_message(
            Topics.TACTICS,
            AgentMessage(
                type="targeting_recommendations",
                source_agent=self.AGENT_TYPE,
                target_agent="tactics",
                payload=recommendations,
            ),
        )
    
    async def _generate_counter_strategy(self, opposition_activity: List[str]) -> None:
        """Generate counter-strategy for opposition activity."""
        system_prompt = """
You are a political strategist. Develop counter-strategies for opposition messaging.
Focus on factual rebuttals and positive framing.
"""
        
        prompt = f"""
Opposition is using these talking points:
{chr(10).join(f'- {a}' for a in opposition_activity)}

Develop a counter-strategy including:
1. Key rebuttals for each point
2. Positive messaging to emphasize
3. Recommended actions for the campaign
"""
        
        response = await self.llm.generate(prompt, system_prompt=system_prompt)
        
        await self.send_message(
            Topics.TACTICS,
            AgentMessage(
                type="counter_strategy",
                source_agent=self.AGENT_TYPE,
                payload={"counter_strategy": response},
            ),
        )
    
    async def _check_policy_windows(self, developments: List[str]) -> None:
        """Check if developments create policy windows."""
        system_prompt = """
You are a policy expert. Identify policy windows - 
opportunities when conditions align for policy change.
"""
        
        prompt = f"""
Recent developments:
{chr(10).join(f'- {d}' for d in developments)}

Do these create any policy windows for wireless power legislation?
If so, describe the opportunity and recommended timing.
"""
        
        response = await self.llm.generate(prompt, system_prompt=system_prompt)
        
        if "opportunity" in response.lower() or "window" in response.lower():
            await self.emit_alert(
                "policy_window",
                "Potential policy window detected",
                {"analysis": response},
                priority=8,
            )
    
    async def _generate_strategy_update(
        self, campaign_id: str, new_info: Dict
    ) -> Dict[str, Any]:
        """Generate strategy update based on new information."""
        prompt = f"""
New information received for campaign:
{new_info}

Generate a strategic response including:
1. How this affects current strategy
2. Recommended adjustments
3. Priority actions
4. Updated timeline if needed
"""
        
        response = await self.llm.generate(prompt)
        
        return {
            "campaign_id": campaign_id,
            "strategy_update": response,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _perform_stakeholder_analysis(self, campaign_id: str) -> Dict[str, Any]:
        """Analyze stakeholders for the campaign."""
        async with get_async_session() as session:
            legislators = await session.execute(select(Legislator))
            all_legislators = legislators.scalars().all()
        
        # Categorize by stance
        supporters = [l for l in all_legislators if l.stance == "support"]
        opponents = [l for l in all_legislators if l.stance == "oppose"]
        undecided = [l for l in all_legislators if l.stance in ("neutral", "unknown")]
        
        return {
            "campaign_id": campaign_id,
            "supporters": len(supporters),
            "opponents": len(opponents),
            "undecided": len(undecided),
            "key_supporters": [l.full_name for l in supporters[:5]],
            "key_opponents": [l.full_name for l in opponents[:5]],
            "swing_votes": [l.full_name for l in undecided[:10]],
        }
    
    async def _generate_targeting_recommendations(
        self, campaign_id: str, action_type: str
    ) -> Dict[str, Any]:
        """Generate recommendations for which legislators to target."""
        async with get_async_session() as session:
            result = await session.execute(
                select(Legislator).where(Legislator.stance.in_(["neutral", "unknown"]))
            )
            swing_votes = result.scalars().all()
        
        # Prioritize by committee membership, party, state
        recommendations = []
        for leg in swing_votes[:20]:
            recommendations.append({
                "legislator_id": str(leg.id),
                "name": leg.full_name,
                "party": leg.party,
                "state": leg.state,
                "chamber": leg.chamber,
                "committees": leg.committees,
                "suggested_approach": f"Emphasize {'innovation' if leg.party == 'R' else 'consumer benefits'}",
            })
        
        return {
            "campaign_id": campaign_id,
            "action_type": action_type,
            "recommendations": recommendations,
        }


async def main():
    from agents.base import run_agent
    agent = StrategyAgent()
    await run_agent(agent)

if __name__ == "__main__":
    asyncio.run(main())
