"""
Base Agent Module

Provides the abstract base class for all advocacy agents.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import AgentEvent, get_async_session
from core.llm import LLMClient, get_llm_client
from core.messaging import AgentMessage, KafkaConsumer, KafkaProducer, Topics

logger = structlog.get_logger()


# =============================================================================
# Agent State
# =============================================================================

class AgentState(BaseModel):
    """Current state of an agent."""
    
    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: str
    status: str = "initializing"  # initializing, running, paused, stopped, error
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    messages_processed: int = 0
    errors_count: int = 0
    current_task: Optional[str] = None


# =============================================================================
# Base Agent
# =============================================================================

class BaseAgent(ABC):
    """
    Abstract base class for all advocacy agents.
    
    Provides common functionality for:
    - Kafka message consumption and production
    - LLM interaction
    - Database access
    - Logging and metrics
    - Lifecycle management
    """
    
    # Override in subclasses
    AGENT_TYPE: str = "base"
    CONSUME_TOPICS: List[str] = []
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        self.state = AgentState(
            agent_id=agent_id or str(uuid4()),
            agent_type=self.AGENT_TYPE,
        )
        
        self._llm = llm_client or get_llm_client()
        self._producer: Optional[KafkaProducer] = None
        self._consumer: Optional[KafkaConsumer] = None
        self._running = False
        self._handlers: Dict[str, Callable] = {}
        
        self.logger = logger.bind(
            agent_type=self.AGENT_TYPE,
            agent_id=self.state.agent_id,
        )
        
        # Register default handlers
        self._register_handlers()
    
    @property
    def llm(self) -> LLMClient:
        """Get the LLM client."""
        return self._llm
    
    # =========================================================================
    # Abstract Methods (must be implemented by subclasses)
    # =========================================================================
    
    @abstractmethod
    def _register_handlers(self) -> None:
        """
        Register message handlers for this agent.
        
        Subclasses should call self.register_handler() for each message type.
        """
        pass
    
    @abstractmethod
    async def process(self, message: AgentMessage) -> None:
        """
        Process a received message.
        
        This is the main entry point for message processing.
        """
        pass
    
    # =========================================================================
    # Lifecycle Methods
    # =========================================================================
    
    async def start(self) -> None:
        """Start the agent."""
        self.logger.info("Starting agent")
        self.state.status = "initializing"
        self.state.started_at = datetime.utcnow()
        
        # Initialize Kafka
        self._producer = KafkaProducer()
        await self._producer.start()
        
        if self.CONSUME_TOPICS:
            self._consumer = KafkaConsumer(
                topics=self.CONSUME_TOPICS,
                group_id=f"{settings.kafka_consumer_group}-{self.AGENT_TYPE}",
            )
            await self._consumer.start()
            
            # Register handlers with consumer
            for message_type, handler in self._handlers.items():
                self._consumer.register_handler(message_type, handler)
        
        self.state.status = "running"
        self._running = True
        
        await self._on_start()
        self.logger.info("Agent started")
    
    async def stop(self) -> None:
        """Stop the agent."""
        self.logger.info("Stopping agent")
        self._running = False
        self.state.status = "stopped"
        
        await self._on_stop()
        
        if self._consumer:
            await self._consumer.stop()
        
        if self._producer:
            await self._producer.stop()
        
        self.logger.info("Agent stopped")
    
    async def run(self) -> None:
        """
        Run the agent's main loop.
        
        This starts the Kafka consumer and processes messages until stopped.
        """
        await self.start()
        
        try:
            if self._consumer:
                await self._consumer.consume()
            else:
                # No consumer, just run the periodic loop
                while self._running:
                    await self._periodic_task()
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info("Agent run cancelled")
        finally:
            await self.stop()
    
    # =========================================================================
    # Handler Registration
    # =========================================================================
    
    def register_handler(
        self,
        message_type: str,
        handler: Optional[Callable] = None,
    ) -> None:
        """
        Register a handler for a message type.
        
        Can be used as a decorator:
            @agent.register_handler("my_message_type")
            async def handle_my_message(message):
                ...
        """
        def decorator(func: Callable) -> Callable:
            self._handlers[message_type] = func
            self.logger.debug("Handler registered", message_type=message_type)
            return func
        
        if handler is not None:
            return decorator(handler)
        return decorator
    
    async def _handle_message(self, message: AgentMessage) -> None:
        """Internal message handler with logging and error tracking."""
        self.state.last_activity = datetime.utcnow()
        self.state.messages_processed += 1
        
        start_time = datetime.utcnow()
        
        try:
            self.logger.debug(
                "Processing message",
                message_id=message.id,
                message_type=message.type,
            )
            
            await self.process(message)
            
            # Log success
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._log_event(
                event_type=f"process_{message.type}",
                description=f"Processed message: {message.type}",
                input_data={"message_id": message.id},
                status="success",
                duration_ms=int(duration),
            )
            
        except Exception as e:
            self.state.errors_count += 1
            self.logger.error(
                "Error processing message",
                message_id=message.id,
                error=str(e),
                exc_info=True,
            )
            
            await self._log_event(
                event_type=f"process_{message.type}",
                description=f"Error processing message: {message.type}",
                input_data={"message_id": message.id},
                status="error",
                error_message=str(e),
            )
    
    # =========================================================================
    # Message Sending
    # =========================================================================
    
    async def send_message(
        self,
        topic: str,
        message: AgentMessage,
    ) -> None:
        """Send a message to a Kafka topic."""
        if not self._producer:
            raise RuntimeError("Agent not started")
        
        await self._producer.send(topic, message)
    
    async def emit_intelligence(self, data: Dict[str, Any]) -> None:
        """Emit an intelligence item."""
        msg = AgentMessage(
            type="intelligence_item",
            source_agent=self.AGENT_TYPE,
            payload=data,
        )
        await self.send_message(Topics.INTELLIGENCE, msg)
    
    async def request_analysis(
        self,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> None:
        """Request analysis from the analysis agent."""
        msg = AgentMessage(
            type="analysis_request",
            source_agent=self.AGENT_TYPE,
            target_agent="analysis",
            payload=data,
            correlation_id=correlation_id,
        )
        await self.send_message(Topics.ANALYSIS, msg)
    
    async def emit_alert(
        self,
        alert_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: int = 5,
    ) -> None:
        """Emit an alert."""
        msg = AgentMessage(
            type="alert",
            source_agent=self.AGENT_TYPE,
            payload={
                "alert_type": alert_type,
                "message": message,
                "data": data or {},
            },
            priority=priority,
        )
        await self.send_message(Topics.ALERTS, msg)
    
    # =========================================================================
    # Database Access
    # =========================================================================
    
    async def _log_event(
        self,
        event_type: str,
        description: str,
        status: str = "success",
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        cost_usd: Optional[float] = None,
    ) -> None:
        """Log an event to the database."""
        try:
            async with get_async_session() as session:
                event = AgentEvent(
                    agent_type=self.AGENT_TYPE,
                    event_type=event_type,
                    description=description,
                    status=status,
                    input_data=input_data or {},
                    output_data=output_data or {},
                    error_message=error_message,
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=duration_ms,
                    tokens_used=tokens_used,
                    cost_usd=cost_usd,
                )
                session.add(event)
                await session.commit()
        except Exception as e:
            self.logger.warning("Failed to log event", error=str(e))
    
    # =========================================================================
    # Hook Methods (override in subclasses)
    # =========================================================================
    
    async def _on_start(self) -> None:
        """Called after the agent starts. Override for custom initialization."""
        pass
    
    async def _on_stop(self) -> None:
        """Called before the agent stops. Override for custom cleanup."""
        pass
    
    async def _periodic_task(self) -> None:
        """
        Called periodically when no messages are being consumed.
        
        Override to add periodic tasks like scheduled scraping.
        """
        pass


# =============================================================================
# Agent Runner
# =============================================================================

async def run_agent(agent: BaseAgent) -> None:
    """
    Run an agent with proper signal handling.
    
    Usage:
        agent = MyAgent()
        asyncio.run(run_agent(agent))
    """
    import signal
    
    loop = asyncio.get_event_loop()
    
    def shutdown():
        logger.info("Shutdown signal received")
        asyncio.create_task(agent.stop())
    
    # Register signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown)
    
    try:
        await agent.run()
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Agent shutdown complete")
