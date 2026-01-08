"""
Tactics Planner Agent

Converts strategy into concrete action items and manages tactical execution.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List

import structlog
from sqlalchemy import select

from agents.base import BaseAgent
from core.database import Action, get_async_session
from core.messaging import AgentMessage, Topics

logger = structlog.get_logger()


class TacticsAgent(BaseAgent):
    """
    Tactics Planner Agent - The Campaign Taskmaster.
    
    Responsibilities:
    - Generate specific action items from strategy
    - Prioritize actions by impact and resources
    - Manage tactical playbook
    - Coordinate timing of actions
    """
    
    AGENT_TYPE = "tactics"
    CONSUME_TOPICS = [Topics.TACTICS, Topics.COMMANDS]
    
    def _register_handlers(self) -> None:
        self.register_handler("strategy_update", self._handle_strategy_update)
        self.register_handler("counter_strategy", self._handle_counter_strategy)
        self.register_handler("targeting_recommendations", self._handle_targeting)
        self.register_handler("generate_actions", self._handle_generate_actions)
    
    async def process(self, message: AgentMessage) -> None:
        handler = self._handlers.get(message.type)
        if handler:
            await handler(message)
    
    async def _handle_strategy_update(self, message: AgentMessage) -> None:
        """Generate actions from strategy update."""
        strategy = message.payload.get("strategy_update", "")
        campaign_id = message.payload.get("campaign_id")
        
        actions = await self._generate_tactical_actions(campaign_id, strategy)
        
        for action in actions:
            await self._create_action(campaign_id, action)
        
        await self.send_message(
            Topics.CONTENT,
            AgentMessage(
                type="content_needs",
                source_agent=self.AGENT_TYPE,
                payload={"actions": actions, "campaign_id": campaign_id},
            ),
        )
    
    async def _handle_counter_strategy(self, message: AgentMessage) -> None:
        """Generate counter-tactics from counter-strategy."""
        counter_strategy = message.payload.get("counter_strategy", "")
        
        actions = await self._generate_counter_actions(counter_strategy)
        
        # Emit urgent content requests
        for action in actions:
            if action.get("content_needed"):
                await self.send_message(
                    Topics.CONTENT,
                    AgentMessage(
                        type="urgent_content_request",
                        source_agent=self.AGENT_TYPE,
                        payload=action,
                        priority=8,
                    ),
                )
    
    async def _handle_targeting(self, message: AgentMessage) -> None:
        """Generate targeted actions for legislators."""
        recommendations = message.payload.get("recommendations", [])
        action_type = message.payload.get("action_type", "outreach")
        
        for rec in recommendations:
            action = await self._create_targeted_action(rec, action_type)
            await self.send_message(
                Topics.CONTENT,
                AgentMessage(
                    type="personalized_content_request",
                    source_agent=self.AGENT_TYPE,
                    payload={
                        "action": action,
                        "legislator": rec,
                    },
                ),
            )
    
    async def _handle_generate_actions(self, message: AgentMessage) -> None:
        """Generate actions for a specific goal."""
        goal = message.payload.get("goal", "")
        constraints = message.payload.get("constraints", {})
        
        actions = await self._generate_goal_actions(goal, constraints)
        
        await self.send_message(
            Topics.TACTICS,
            AgentMessage(
                type="actions_generated",
                source_agent=self.AGENT_TYPE,
                correlation_id=message.correlation_id,
                payload={"actions": actions},
            ),
        )
    
    async def _generate_tactical_actions(
        self, campaign_id: str, strategy: str
    ) -> List[Dict[str, Any]]:
        """Generate tactical actions from strategy."""
        prompt = f"""
Based on this strategy:
{strategy}

Generate specific tactical actions. For each action include:
- action_type (phone_bank, letter_campaign, social_blitz, press_event, lobby_day)
- title
- description
- priority (1-10)
- estimated_hours
- content_needed (true/false)

Return as JSON array.
"""
        
        response = await self.llm.generate(prompt)
        
        try:
            import json
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        return [{
            "action_type": "social_blitz",
            "title": "Social Media Response",
            "description": "Respond to developments on social media",
            "priority": 5,
            "estimated_hours": 2,
            "content_needed": True,
        }]
    
    async def _generate_counter_actions(self, counter_strategy: str) -> List[Dict]:
        """Generate counter-actions from counter-strategy."""
        return [{
            "action_type": "rapid_response",
            "title": "Counter Opposition Messaging",
            "description": counter_strategy[:200],
            "priority": 8,
            "content_needed": True,
            "content_type": "rebuttal",
        }]
    
    async def _create_targeted_action(
        self, rec: Dict, action_type: str
    ) -> Dict[str, Any]:
        """Create a targeted action for a legislator."""
        return {
            "action_type": action_type,
            "title": f"Outreach to {rec.get('name')}",
            "target_legislator": rec.get("legislator_id"),
            "suggested_approach": rec.get("suggested_approach"),
            "priority": 7,
            "content_needed": True,
        }
    
    async def _generate_goal_actions(
        self, goal: str, constraints: Dict
    ) -> List[Dict[str, Any]]:
        """Generate actions to achieve a specific goal."""
        prompt = f"""
Goal: {goal}
Constraints: {constraints}

Generate 5-10 tactical actions to achieve this goal.
Consider: phone banks, emails, social media, press, lobby visits.
"""
        
        response = await self.llm.generate(prompt)
        
        return [{"description": response, "goal": goal}]
    
    async def _create_action(self, campaign_id: str, action_data: Dict) -> None:
        """Create action in database."""
        async with get_async_session() as session:
            action = Action(
                campaign_id=campaign_id if campaign_id else None,
                action_type=action_data.get("action_type", "general"),
                title=action_data.get("title", "Action"),
                description=action_data.get("description"),
                priority=action_data.get("priority", 5),
                estimated_time_hours=action_data.get("estimated_hours"),
                status="pending",
            )
            session.add(action)
            await session.commit()


async def main():
    from agents.base import run_agent
    await run_agent(TacticsAgent())

if __name__ == "__main__":
    asyncio.run(main())
