"""
Settings API Routes

Provides endpoints for managing system settings and API keys.
Settings are encrypted at rest using Fernet encryption.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.connection import get_async_session
from core.database.models import SystemSetting
from core.security.encryption import encrypt_value, decrypt_value, mask_secret, is_valid_api_key


router = APIRouter(prefix="/settings", tags=["settings"])


# =============================================================================
# Pydantic Models
# =============================================================================

class SettingResponse(BaseModel):
    """Response model for a single setting (value masked if secret)."""
    id: UUID
    key: str
    category: str
    display_name: Optional[str]
    description: Optional[str]
    value: str  # Masked if is_secret
    is_secret: bool
    is_configured: bool
    is_required: bool
    updated_at: datetime


class SettingUpdate(BaseModel):
    """Request model for updating a setting value."""
    value: str = Field(..., min_length=1)


class SettingCreate(BaseModel):
    """Request model for creating a new setting."""
    key: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    value: str = Field(..., min_length=1)
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_secret: bool = True
    is_required: bool = False


class SettingsBulkUpdate(BaseModel):
    """Request model for bulk updating settings."""
    settings: Dict[str, str]  # key -> value


class SettingsCategoryResponse(BaseModel):
    """Response model for settings grouped by category."""
    category: str
    settings: List[SettingResponse]


class ConnectionTestResult(BaseModel):
    """Response model for connection test results."""
    key: str
    success: bool
    message: str


# =============================================================================
# Default Settings Definition
# =============================================================================

DEFAULT_SETTINGS = [
    # LLM Providers
    {"key": "openai_api_key", "category": "llm", "display_name": "OpenAI API Key", 
     "description": "API key for OpenAI GPT models", "is_required": True},
    {"key": "anthropic_api_key", "category": "llm", "display_name": "Anthropic API Key",
     "description": "API key for Anthropic Claude models", "is_required": False},
    {"key": "llm_provider", "category": "llm", "display_name": "Primary LLM Provider",
     "description": "Default LLM provider (openai or anthropic)", "is_required": True, "is_secret": False},
    
    # External APIs
    {"key": "congress_api_key", "category": "external_api", "display_name": "Congress.gov API Key",
     "description": "API key for accessing Congress.gov data", "is_required": True},
    {"key": "twitter_bearer_token", "category": "external_api", "display_name": "Twitter Bearer Token",
     "description": "Bearer token for Twitter/X API v2", "is_required": False},
    {"key": "reddit_client_id", "category": "external_api", "display_name": "Reddit Client ID",
     "description": "OAuth client ID for Reddit API", "is_required": False},
    {"key": "reddit_client_secret", "category": "external_api", "display_name": "Reddit Client Secret",
     "description": "OAuth client secret for Reddit API", "is_required": False},
    {"key": "newsapi_key", "category": "external_api", "display_name": "NewsAPI Key",
     "description": "API key for NewsAPI.org", "is_required": False},
    
    # Communication
    {"key": "sendgrid_api_key", "category": "communication", "display_name": "SendGrid API Key",
     "description": "API key for SendGrid email service", "is_required": False},
    {"key": "sendgrid_from_email", "category": "communication", "display_name": "SendGrid From Email",
     "description": "Verified sender email for SendGrid", "is_required": False, "is_secret": False},
    {"key": "twilio_account_sid", "category": "communication", "display_name": "Twilio Account SID",
     "description": "Twilio account SID for SMS", "is_required": False},
    {"key": "twilio_auth_token", "category": "communication", "display_name": "Twilio Auth Token",
     "description": "Twilio auth token for SMS", "is_required": False},
    
    # Messaging
    {"key": "kafka_bootstrap_servers", "category": "messaging", "display_name": "Kafka Bootstrap Servers",
     "description": "Comma-separated list of Kafka brokers", "is_required": False, "is_secret": False},
    {"key": "redis_dsn", "category": "messaging", "display_name": "Redis Connection URL",
     "description": "Redis connection string for caching", "is_required": False},
]


# =============================================================================
# Initialization
# =============================================================================

async def initialize_default_settings(session: AsyncSession) -> None:
    """
    Initialize database with default settings if they don't exist.
    Called on application startup.
    """
    for setting_def in DEFAULT_SETTINGS:
        existing = await session.execute(
            select(SystemSetting).where(SystemSetting.key == setting_def["key"])
        )
        if not existing.scalar_one_or_none():
            setting = SystemSetting(
                key=setting_def["key"],
                category=setting_def["category"],
                display_name=setting_def.get("display_name", setting_def["key"]),
                description=setting_def.get("description", ""),
                value=encrypt_value(""),  # Empty encrypted value
                is_secret=setting_def.get("is_secret", True),
                is_required=setting_def.get("is_required", False),
                is_configured=False,
            )
            session.add(setting)
    
    await session.commit()


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/", response_model=List[SettingsCategoryResponse])
async def list_settings(
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all settings grouped by category.
    Secret values are masked.
    """
    result = await session.execute(
        select(SystemSetting).order_by(SystemSetting.category, SystemSetting.key)
    )
    settings = result.scalars().all()
    
    # Group by category
    categories: Dict[str, List[SettingResponse]] = {}
    for setting in settings:
        if setting.category not in categories:
            categories[setting.category] = []
        
        # Mask secret values
        display_value = ""
        if setting.is_configured:
            try:
                decrypted = decrypt_value(setting.value)
                display_value = mask_secret(decrypted) if setting.is_secret else decrypted
            except:
                display_value = "***error***"
        
        categories[setting.category].append(SettingResponse(
            id=setting.id,
            key=setting.key,
            category=setting.category,
            display_name=setting.display_name,
            description=setting.description,
            value=display_value,
            is_secret=setting.is_secret,
            is_configured=setting.is_configured,
            is_required=setting.is_required,
            updated_at=setting.updated_at,
        ))
    
    return [
        SettingsCategoryResponse(category=cat, settings=sett)
        for cat, sett in categories.items()
    ]


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Get a single setting by key (masked if secret)."""
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    display_value = ""
    if setting.is_configured:
        try:
            decrypted = decrypt_value(setting.value)
            display_value = mask_secret(decrypted) if setting.is_secret else decrypted
        except:
            display_value = "***error***"
    
    return SettingResponse(
        id=setting.id,
        key=setting.key,
        category=setting.category,
        display_name=setting.display_name,
        description=setting.description,
        value=display_value,
        is_secret=setting.is_secret,
        is_configured=setting.is_configured,
        is_required=setting.is_required,
        updated_at=setting.updated_at,
    )


@router.put("/{key}")
async def update_setting(
    key: str,
    data: SettingUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Update a single setting value."""
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    # Validate API key format if applicable
    if setting.is_secret and not is_valid_api_key(key, data.value):
        # Still allow saving, just warn
        pass
    
    # Encrypt and save
    setting.value = encrypt_value(data.value)
    setting.is_configured = True
    setting.updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "key": key, "message": "Setting updated successfully"}


@router.post("/bulk")
async def bulk_update_settings(
    data: SettingsBulkUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Update multiple settings at once."""
    updated = []
    errors = []
    
    for key, value in data.settings.items():
        result = await session.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        
        if not setting:
            errors.append({"key": key, "error": "Setting not found"})
            continue
        
        if value:  # Only update if value provided
            setting.value = encrypt_value(value)
            setting.is_configured = True
            setting.updated_at = datetime.utcnow()
            updated.append(key)
    
    await session.commit()
    
    return {
        "success": len(errors) == 0,
        "updated": updated,
        "errors": errors,
    }


@router.delete("/{key}")
async def clear_setting(
    key: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Clear a setting value (set to empty)."""
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    setting.value = encrypt_value("")
    setting.is_configured = False
    setting.updated_at = datetime.utcnow()
    
    await session.commit()
    
    return {"success": True, "key": key, "message": "Setting cleared"}


@router.post("/test/{key}", response_model=ConnectionTestResult)
async def test_setting(
    key: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Test a setting by attempting to use it."""
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    if not setting.is_configured:
        return ConnectionTestResult(
            key=key,
            success=False,
            message="Setting is not configured",
        )
    
    try:
        value = decrypt_value(setting.value)
        
        # Test based on key type
        if key == "openai_api_key":
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {value}"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ConnectionTestResult(key=key, success=True, message="OpenAI API key is valid")
                else:
                    return ConnectionTestResult(key=key, success=False, message=f"OpenAI API returned {resp.status_code}")
        
        elif key == "congress_api_key":
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://api.congress.gov/v3/bill?api_key={value}&limit=1",
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ConnectionTestResult(key=key, success=True, message="Congress.gov API key is valid")
                else:
                    return ConnectionTestResult(key=key, success=False, message=f"Congress.gov API returned {resp.status_code}")
        
        else:
            # Generic validation - just check it's not empty
            if value and len(value) > 5:
                return ConnectionTestResult(key=key, success=True, message="Setting appears valid (not tested)")
            else:
                return ConnectionTestResult(key=key, success=False, message="Setting value is too short")
    
    except Exception as e:
        return ConnectionTestResult(key=key, success=False, message=f"Test failed: {str(e)}")


# =============================================================================
# Internal Helper (for agents to get decrypted values)
# =============================================================================

async def get_setting_value(key: str, session: AsyncSession) -> Optional[str]:
    """
    Get decrypted setting value for internal use.
    Used by agents to retrieve API keys.
    
    Returns None if not configured.
    """
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting or not setting.is_configured:
        return None
    
    try:
        return decrypt_value(setting.value)
    except:
        return None
