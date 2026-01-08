"""
Kafka Messaging Client

Provides async Kafka producer and consumer for inter-agent communication.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import UUID, uuid4

import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import BaseModel, Field

from core.config import settings

logger = structlog.get_logger()


# =============================================================================
# Message Types
# =============================================================================

class AgentMessage(BaseModel):
    """
    Standard message format for inter-agent communication.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str  # Message type (e.g., "intelligence_item", "content_request", etc.)
    source_agent: str  # Agent that sent the message
    target_agent: Optional[str] = None  # Specific target or None for broadcast
    
    # Payload
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    correlation_id: Optional[str] = None  # For request-response patterns
    priority: int = Field(default=5, ge=1, le=10)  # 1 = lowest, 10 = highest
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
    
    def to_json(self) -> bytes:
        """Serialize message to JSON bytes."""
        return self.model_dump_json().encode("utf-8")
    
    @classmethod
    def from_json(cls, data: bytes) -> "AgentMessage":
        """Deserialize message from JSON bytes."""
        return cls.model_validate_json(data)


# =============================================================================
# Topic Names
# =============================================================================

class Topics:
    """Kafka topic names for the advocacy system."""
    
    # Agent communication topics
    INTELLIGENCE = f"{settings.kafka_topic_prefix}.intelligence"
    ANALYSIS = f"{settings.kafka_topic_prefix}.analysis"
    STRATEGY = f"{settings.kafka_topic_prefix}.strategy"
    TACTICS = f"{settings.kafka_topic_prefix}.tactics"
    CONTENT = f"{settings.kafka_topic_prefix}.content"
    DISTRIBUTION = f"{settings.kafka_topic_prefix}.distribution"
    FEEDBACK = f"{settings.kafka_topic_prefix}.feedback"
    
    # Special topics
    ALERTS = f"{settings.kafka_topic_prefix}.alerts"
    COMMANDS = f"{settings.kafka_topic_prefix}.commands"
    EVENTS = f"{settings.kafka_topic_prefix}.events"
    
    @classmethod
    def all_topics(cls) -> List[str]:
        """Get all topic names."""
        return [
            cls.INTELLIGENCE,
            cls.ANALYSIS,
            cls.STRATEGY,
            cls.TACTICS,
            cls.CONTENT,
            cls.DISTRIBUTION,
            cls.FEEDBACK,
            cls.ALERTS,
            cls.COMMANDS,
            cls.EVENTS,
        ]


# =============================================================================
# Kafka Producer
# =============================================================================

class KafkaProducer:
    """
    Async Kafka producer for sending messages between agents.
    """
    
    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
        self._started = False
    
    async def start(self) -> None:
        """Start the Kafka producer."""
        if self._started:
            return
        
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: v if isinstance(v, bytes) else json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retry_backoff_ms=100,
            max_request_size=10485760,  # 10MB
        )
        await self._producer.start()
        self._started = True
        logger.info("Kafka producer started", servers=settings.kafka_bootstrap_servers)
    
    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self._producer and self._started:
            await self._producer.stop()
            self._started = False
            logger.info("Kafka producer stopped")
    
    async def send(
        self,
        topic: str,
        message: AgentMessage,
        key: Optional[str] = None,
    ) -> None:
        """
        Send a message to a Kafka topic.
        
        Args:
            topic: The topic to send to
            message: The AgentMessage to send
            key: Optional partition key
        """
        if not self._started:
            await self.start()
        
        try:
            await self._producer.send_and_wait(
                topic=topic,
                value=message.to_json(),
                key=key or message.id,
            )
            logger.debug(
                "Message sent",
                topic=topic,
                message_id=message.id,
                type=message.type,
            )
        except Exception as e:
            logger.error(
                "Failed to send message",
                topic=topic,
                message_id=message.id,
                error=str(e),
            )
            raise
    
    async def send_intelligence(self, payload: Dict[str, Any], source: str = "monitoring") -> None:
        """Send an intelligence item."""
        msg = AgentMessage(
            type="intelligence_item",
            source_agent=source,
            payload=payload,
        )
        await self.send(Topics.INTELLIGENCE, msg)
    
    async def send_analysis_request(
        self,
        payload: Dict[str, Any],
        source: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Request analysis from the analysis agent."""
        msg = AgentMessage(
            type="analysis_request",
            source_agent=source,
            target_agent="analysis",
            payload=payload,
            correlation_id=correlation_id,
        )
        await self.send(Topics.ANALYSIS, msg)
    
    async def send_content_request(
        self,
        content_type: str,
        payload: Dict[str, Any],
        source: str,
    ) -> None:
        """Request content creation."""
        msg = AgentMessage(
            type="content_request",
            source_agent=source,
            target_agent="content",
            payload={"content_type": content_type, **payload},
        )
        await self.send(Topics.CONTENT, msg)
    
    async def send_alert(
        self,
        alert_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        source: str = "system",
    ) -> None:
        """Send an alert notification."""
        msg = AgentMessage(
            type="alert",
            source_agent=source,
            payload={
                "alert_type": alert_type,
                "message": message,
                "data": data or {},
            },
            priority=priority,
        )
        await self.send(Topics.ALERTS, msg)
    
    async def __aenter__(self) -> "KafkaProducer":
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()


# =============================================================================
# Kafka Consumer
# =============================================================================

class KafkaConsumer:
    """
    Async Kafka consumer for receiving messages.
    """
    
    def __init__(
        self,
        topics: List[str],
        group_id: Optional[str] = None,
    ):
        self.topics = topics
        self.group_id = group_id or settings.kafka_consumer_group
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._started = False
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def start(self) -> None:
        """Start the Kafka consumer."""
        if self._started:
            return
        
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            auto_commit_interval_ms=5000,
            value_deserializer=lambda v: AgentMessage.from_json(v),
        )
        await self._consumer.start()
        self._started = True
        logger.info(
            "Kafka consumer started",
            topics=self.topics,
            group_id=self.group_id,
        )
    
    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        self._running = False
        if self._consumer and self._started:
            await self._consumer.stop()
            self._started = False
            logger.info("Kafka consumer stopped")
    
    def register_handler(
        self,
        message_type: str,
        handler: Callable[[AgentMessage], Any],
    ) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: The message type to handle
            handler: Async function that takes an AgentMessage
        """
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        self._handlers[message_type].append(handler)
        logger.debug("Handler registered", message_type=message_type)
    
    async def consume(self) -> None:
        """
        Start consuming messages and dispatching to handlers.
        
        This is a blocking operation that runs until stop() is called.
        """
        if not self._started:
            await self.start()
        
        self._running = True
        logger.info("Starting message consumption")
        
        try:
            async for record in self._consumer:
                if not self._running:
                    break
                
                message: AgentMessage = record.value
                logger.debug(
                    "Message received",
                    topic=record.topic,
                    message_id=message.id,
                    type=message.type,
                )
                
                # Dispatch to handlers
                handlers = self._handlers.get(message.type, [])
                
                # Also check for wildcard handlers
                handlers.extend(self._handlers.get("*", []))
                
                if not handlers:
                    logger.warning(
                        "No handler for message type",
                        message_type=message.type,
                    )
                    continue
                
                for handler in handlers:
                    try:
                        result = handler(message)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        logger.error(
                            "Handler error",
                            message_type=message.type,
                            error=str(e),
                            exc_info=True,
                        )
        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        finally:
            self._running = False
    
    async def __aenter__(self) -> "KafkaConsumer":
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()


# =============================================================================
# Singleton Instance
# =============================================================================

_producer_instance: Optional[KafkaProducer] = None


async def get_producer() -> KafkaProducer:
    """Get or create the global Kafka producer instance."""
    global _producer_instance
    if _producer_instance is None:
        _producer_instance = KafkaProducer()
        await _producer_instance.start()
    return _producer_instance


async def shutdown_producer() -> None:
    """Shutdown the global Kafka producer."""
    global _producer_instance
    if _producer_instance is not None:
        await _producer_instance.stop()
        _producer_instance = None
