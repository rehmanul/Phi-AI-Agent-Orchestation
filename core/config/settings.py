"""
Configuration Settings Module

Centralized configuration management using Pydantic Settings.
All environment variables are validated and typed.
"""

from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Settings are grouped by functionality for easier management.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # =========================================================================
    # Application Settings
    # =========================================================================
    app_name: str = Field(default="advocacy-orchestration", description="Application name")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Current environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # =========================================================================
    # LLM Configuration
    # =========================================================================
    llm_provider: Literal["openai", "anthropic"] = Field(
        default="openai",
        description="Primary LLM provider"
    )
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model"
    )
    
    # =========================================================================
    # Database Configuration
    # =========================================================================
    # PostgreSQL
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="advocacy_db")
    postgres_user: str = Field(default="advocacy_user")
    postgres_password: str = Field(default="")
    database_url: Optional[str] = Field(default=None, description="Full database URL")
    
    @property
    def postgres_dsn(self) -> str:
        """Construct PostgreSQL connection string."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def postgres_sync_dsn(self) -> str:
        """Construct synchronous PostgreSQL connection string."""
        return self.postgres_dsn.replace("postgresql+asyncpg://", "postgresql://")
    
    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: Optional[str] = Field(default=None)
    redis_url: Optional[str] = Field(default=None)
    
    @property
    def redis_dsn(self) -> str:
        """Construct Redis connection string."""
        if self.redis_url:
            return self.redis_url
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/0"
    
    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="")
    
    # =========================================================================
    # Message Queue (Kafka)
    # =========================================================================
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_consumer_group: str = Field(default="advocacy-agents")
    kafka_topic_prefix: str = Field(default="advocacy")
    
    # =========================================================================
    # Object Storage (S3/MinIO)
    # =========================================================================
    s3_endpoint: str = Field(default="http://localhost:9000")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")
    s3_bucket: str = Field(default="advocacy-content")
    s3_region: str = Field(default="us-east-1")
    
    # =========================================================================
    # External API Keys
    # =========================================================================
    # Congress.gov
    congress_api_key: Optional[str] = Field(default=None)
    congress_api_base_url: str = Field(default="https://api.congress.gov/v3")
    
    # Twitter/X
    twitter_api_key: Optional[str] = Field(default=None)
    twitter_api_secret: Optional[str] = Field(default=None)
    twitter_access_token: Optional[str] = Field(default=None)
    twitter_access_secret: Optional[str] = Field(default=None)
    twitter_bearer_token: Optional[str] = Field(default=None)
    
    # Reddit
    reddit_client_id: Optional[str] = Field(default=None)
    reddit_client_secret: Optional[str] = Field(default=None)
    reddit_user_agent: str = Field(default="AdvocacyBot/1.0")
    
    # Facebook
    facebook_access_token: Optional[str] = Field(default=None)
    facebook_page_id: Optional[str] = Field(default=None)
    
    # News
    newsapi_key: Optional[str] = Field(default=None)
    google_news_rss_url: str = Field(default="https://news.google.com/rss")
    
    # Email (SendGrid)
    sendgrid_api_key: Optional[str] = Field(default=None)
    sendgrid_from_email: str = Field(default="noreply@example.com")
    sendgrid_from_name: str = Field(default="Advocacy Campaign")
    
    # Voice/SMS (Twilio)
    twilio_account_sid: Optional[str] = Field(default=None)
    twilio_auth_token: Optional[str] = Field(default=None)
    twilio_phone_number: Optional[str] = Field(default=None)
    
    # =========================================================================
    # API Server Settings
    # =========================================================================
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_workers: int = Field(default=4)
    api_secret_key: str = Field(
        default="change-this-in-production",
        description="JWT secret key"
    )
    api_access_token_expire_minutes: int = Field(default=60)
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    # =========================================================================
    # Dashboard Settings
    # =========================================================================
    dashboard_url: str = Field(default="http://localhost:3000")
    
    # =========================================================================
    # Monitoring
    # =========================================================================
    prometheus_enabled: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)
    sentry_dsn: Optional[str] = Field(default=None)
    
    # =========================================================================
    # Agent-specific Settings
    # =========================================================================
    agent_type: Optional[str] = Field(default=None, description="Type of agent when running as worker")
    
    # Monitoring intervals (seconds)
    monitoring_legislative_interval: int = Field(default=3600, description="Legislative check interval")
    monitoring_news_interval: int = Field(default=900, description="News check interval (15 min)")
    monitoring_social_interval: int = Field(default=300, description="Social media check interval (5 min)")
    
    def get_llm_api_key(self) -> str:
        """Get API key for the configured LLM provider."""
        if self.llm_provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return self.openai_api_key
        elif self.llm_provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return self.anthropic_api_key
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
    
    def get_llm_model(self) -> str:
        """Get model name for the configured LLM provider."""
        if self.llm_provider == "openai":
            return self.openai_model
        elif self.llm_provider == "anthropic":
            return self.anthropic_model
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Convenience export
settings = get_settings()
