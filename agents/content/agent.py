"""
Content Creator Agent

Generates all campaign communications including press releases, fact sheets,
op-eds, social media content, and personalized messages.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import select

from agents.base import BaseAgent
from core.database import ContentItem, Legislator, get_async_session
from core.llm import CommunicationsLLM, PolicyWriterLLM, SocialMediaLLM
from core.messaging import AgentMessage, Topics

logger = structlog.get_logger()


class ContentAgent(BaseAgent):
    """
    Content Creator Agent - The Campaign Writer.
    
    Sub-components:
    - Policy Writer: Fact sheets, white papers, testimony
    - Communications: Press releases, op-eds, emails
    - Social Media: Tweets, threads, posts
    """
    
    AGENT_TYPE = "content"
    CONSUME_TOPICS = [Topics.CONTENT, Topics.COMMANDS]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._policy_llm = PolicyWriterLLM()
        self._comms_llm = CommunicationsLLM()
        self._social_llm = SocialMediaLLM()
    
    def _register_handlers(self) -> None:
        self.register_handler("content_needs", self._handle_content_needs)
        self.register_handler("urgent_content_request", self._handle_urgent_request)
        self.register_handler("personalized_content_request", self._handle_personalized)
        self.register_handler("generate_content", self._handle_generate_content)
    
    async def process(self, message: AgentMessage) -> None:
        handler = self._handlers.get(message.type)
        if handler:
            await handler(message)
    
    async def _handle_content_needs(self, message: AgentMessage) -> None:
        """Generate content for campaign actions."""
        actions = message.payload.get("actions", [])
        campaign_id = message.payload.get("campaign_id")
        
        for action in actions:
            if action.get("content_needed"):
                content = await self._generate_action_content(action)
                await self._save_content(campaign_id, content)
    
    async def _handle_urgent_request(self, message: AgentMessage) -> None:
        """Handle urgent content request (e.g., rapid response)."""
        content_type = message.payload.get("content_type", "rebuttal")
        description = message.payload.get("description", "")
        
        if content_type == "rebuttal":
            content = await self._generate_rebuttal(description)
        else:
            content = await self._generate_rapid_response(description)
        
        # Send directly to distribution
        await self.send_message(
            Topics.DISTRIBUTION,
            AgentMessage(
                type="urgent_content_ready",
                source_agent=self.AGENT_TYPE,
                payload=content,
                priority=9,
            ),
        )
    
    async def _handle_personalized(self, message: AgentMessage) -> None:
        """Generate personalized content for a legislator."""
        action = message.payload.get("action", {})
        legislator = message.payload.get("legislator", {})
        
        content = await self._generate_personalized_content(action, legislator)
        
        await self.send_message(
            Topics.DISTRIBUTION,
            AgentMessage(
                type="personalized_content_ready",
                source_agent=self.AGENT_TYPE,
                payload={
                    "content": content,
                    "target_legislator": legislator.get("legislator_id"),
                },
            ),
        )
    
    async def _handle_generate_content(self, message: AgentMessage) -> None:
        """Generate specific content on demand."""
        content_type = message.payload.get("content_type")
        params = message.payload.get("params", {})
        
        if content_type == "fact_sheet":
            content = await self._policy_llm.write_fact_sheet(
                params.get("topic", "Wireless Power Technology"),
                params.get("key_points", []),
                params.get("audience", "legislators"),
            )
        elif content_type == "press_release":
            content = await self._comms_llm.write_press_release(
                params.get("headline", ""),
                params.get("key_facts", []),
                params.get("quotes"),
            )
        elif content_type == "op_ed":
            content = await self._comms_llm.write_op_ed(
                params.get("topic", ""),
                params.get("thesis", ""),
                params.get("supporting_points", []),
                params.get("author_perspective", ""),
            )
        elif content_type == "tweets":
            content = await self._social_llm.generate_tweets(
                params.get("topic", ""),
                params.get("key_message", ""),
                params.get("num_variants", 5),
            )
        elif content_type == "thread":
            content = await self._social_llm.generate_thread(
                params.get("topic", ""),
                params.get("key_points", []),
            )
        else:
            content = await self.llm.generate(
                f"Generate {content_type} content about: {params}"
            )
        
        await self.send_message(
            Topics.CONTENT,
            AgentMessage(
                type="content_generated",
                source_agent=self.AGENT_TYPE,
                correlation_id=message.correlation_id,
                payload={"content_type": content_type, "content": content},
            ),
        )
    
    async def _generate_action_content(self, action: Dict) -> Dict[str, Any]:
        """Generate content for a specific action."""
        action_type = action.get("action_type", "general")
        
        if action_type == "social_blitz":
            tweets = await self._social_llm.generate_tweets(
                action.get("title", "Wireless Power Policy"),
                action.get("description", "Support clean energy innovation"),
                num_variants=5,
            )
            return {
                "content_type": "tweets",
                "body": "\n---\n".join(tweets),
                "title": action.get("title"),
            }
        
        elif action_type == "letter_campaign":
            letter = await self.llm.generate(f"""
Write a constituent letter template about: {action.get('title')}
Purpose: {action.get('description')}

Include:
- Personal opening (with placeholder for name)
- Why this matters to constituents
- Specific ask (support/oppose bill)
- Closing with contact info placeholder
""")
            return {
                "content_type": "letter_template",
                "body": letter,
                "title": f"Letter: {action.get('title')}",
            }
        
        elif action_type == "press_event":
            press = await self._comms_llm.write_press_release(
                action.get("title", "Advocacy Event"),
                [action.get("description", "")],
            )
            return {
                "content_type": "press_release",
                "body": press,
                "title": action.get("title"),
            }
        
        else:
            return {
                "content_type": "general",
                "body": action.get("description", ""),
                "title": action.get("title", "Action Content"),
            }
    
    async def _generate_rebuttal(self, opposition_content: str) -> Dict[str, Any]:
        """Generate rebuttal to opposition content."""
        rebuttal = await self.llm.generate(f"""
Generate a factual rebuttal to this opposition claim:
{opposition_content[:500]}

The rebuttal should:
1. Acknowledge the concern
2. Provide factual corrections
3. Redirect to positive messaging about wireless power benefits
4. Be suitable for social media (under 280 chars) AND a longer format
""")
        
        return {
            "content_type": "rebuttal",
            "body": rebuttal,
            "title": "Rapid Response Rebuttal",
            "priority": "urgent",
        }
    
    async def _generate_rapid_response(self, situation: str) -> Dict[str, Any]:
        """Generate rapid response content."""
        response = await self.llm.generate(f"""
Generate rapid response content for: {situation}

Create:
1. Tweet (under 280 chars)
2. Longer statement (2-3 paragraphs)
3. Key talking points (3-5 bullets)
""")
        
        return {
            "content_type": "rapid_response",
            "body": response,
            "title": "Rapid Response",
        }
    
    async def _generate_personalized_content(
        self, action: Dict, legislator: Dict
    ) -> Dict[str, Any]:
        """Generate content personalized for a specific legislator."""
        leg_name = legislator.get("name", "the legislator")
        approach = legislator.get("suggested_approach", "innovation and consumer benefits")
        state = legislator.get("state", "")
        
        content = await self.llm.generate(f"""
Generate personalized outreach content for {leg_name} from {state}.

Action: {action.get('title')}
Suggested approach: {approach}

Create:
1. Personalized email draft
2. Brief talking points if meeting in person
3. Social media mention if appropriate
""")
        
        return {
            "content_type": "personalized_outreach",
            "body": content,
            "title": f"Outreach to {leg_name}",
            "target_legislator": legislator.get("legislator_id"),
        }
    
    async def _save_content(
        self, campaign_id: Optional[str], content_data: Dict
    ) -> None:
        """Save content to database."""
        async with get_async_session() as session:
            item = ContentItem(
                campaign_id=campaign_id if campaign_id else None,
                content_type=content_data.get("content_type", "general"),
                title=content_data.get("title"),
                body=content_data.get("body", ""),
                status="draft",
            )
            session.add(item)
            await session.commit()


async def main():
    from agents.base import run_agent
    await run_agent(ContentAgent())

if __name__ == "__main__":
    asyncio.run(main())
