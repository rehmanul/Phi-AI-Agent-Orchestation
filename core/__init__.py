"""
AI Agent Orchestration - Core Module

This module provides shared utilities, configuration, and base classes
for the multi-agent advocacy system.
"""

from core.config.settings import settings
from core.database.connection import get_db, get_async_db
from core.messaging.kafka_client import KafkaProducer, KafkaConsumer
from core.llm.client import get_llm_client

__all__ = [
    "settings",
    "get_db",
    "get_async_db",
    "KafkaProducer",
    "KafkaConsumer",
    "get_llm_client",
]
