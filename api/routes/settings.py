"""
Settings API Routes (File-Based)

Provides endpoints for managing system settings and API keys.
Settings are stored in an encrypted JSON file - NO DATABASE REQUIRED.
"""

from typing import Dict, List

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.settings import get_settings_store, get_setting_value


router = APIRouter(prefix="/settings", tags=["settings"])


# =============================================================================
# Pydantic Models
# =============================================================================

class SettingResponse(BaseModel):
    """Response model for a single setting."""
    id: str
    key: str
    category: str
    display_name: str
    description: str
    value: str  # Masked if secret
    is_secret: bool
    is_configured: bool
    is_required: bool
    updated_at: str


class SettingsCategoryResponse(BaseModel):
    """Response model for settings grouped by category."""
    category: str
    settings: List[SettingResponse]


class SettingUpdate(BaseModel):
    """Request model for updating a setting."""
    value: str = Field(..., min_length=1)


class SettingsBulkUpdate(BaseModel):
    """Request model for bulk updating settings."""
    settings: Dict[str, str]


class ConnectionTestResult(BaseModel):
    """Response model for connection test."""
    key: str
    success: bool
    message: str


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/", response_model=List[SettingsCategoryResponse])
async def list_settings():
    """
    List all settings grouped by category.
    Secret values are masked.
    """
    store = get_settings_store()
    return store.get_all()


@router.get("/{key}")
async def get_setting(key: str):
    """Get a single setting by key (masked if secret)."""
    store = get_settings_store()
    setting = store.get(key)
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    return setting


@router.put("/{key}")
async def update_setting(key: str, data: SettingUpdate):
    """Update a single setting value."""
    store = get_settings_store()
    
    if not store.set(key, data.value):
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    return {"success": True, "key": key, "message": "Setting updated successfully"}


@router.post("/bulk")
async def bulk_update_settings(data: SettingsBulkUpdate):
    """Update multiple settings at once."""
    store = get_settings_store()
    results = store.set_many(data.settings)
    
    updated = [k for k, v in results.items() if v]
    errors = [{"key": k, "error": "Setting not found"} for k, v in results.items() if not v]
    
    return {
        "success": len(errors) == 0,
        "updated": updated,
        "errors": errors,
    }


@router.delete("/{key}")
async def clear_setting(key: str):
    """Clear a setting value (set to empty)."""
    store = get_settings_store()
    
    if not store.clear(key):
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    return {"success": True, "key": key, "message": "Setting cleared"}


@router.post("/test/{key}", response_model=ConnectionTestResult)
async def test_setting(key: str):
    """Test a setting by attempting to use it."""
    value = get_setting_value(key)
    
    if not value:
        return ConnectionTestResult(
            key=key,
            success=False,
            message="Setting is not configured",
        )
    
    try:
        if key == "openai_api_key":
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
        
        elif key == "anthropic_api_key":
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={
                        "x-api-key": value,
                        "anthropic-version": "2023-06-01",
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ConnectionTestResult(key=key, success=True, message="Anthropic API key is valid")
                else:
                    return ConnectionTestResult(key=key, success=False, message=f"Anthropic API returned {resp.status_code}")
        
        elif key == "congress_api_key":
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://api.congress.gov/v3/bill?api_key={value}&limit=1",
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ConnectionTestResult(key=key, success=True, message="Congress.gov API key is valid")
                else:
                    return ConnectionTestResult(key=key, success=False, message=f"Congress.gov API returned {resp.status_code}")
        
        elif key == "newsapi_key":
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey={value}",
                    timeout=10,
                )
                if resp.status_code == 200:
                    return ConnectionTestResult(key=key, success=True, message="NewsAPI key is valid")
                else:
                    return ConnectionTestResult(key=key, success=False, message=f"NewsAPI returned {resp.status_code}")
        
        else:
            # Generic validation - just check it's not empty
            if len(value) > 5:
                return ConnectionTestResult(key=key, success=True, message="Setting is configured (not tested)")
            else:
                return ConnectionTestResult(key=key, success=False, message="Setting value appears too short")
    
    except Exception as e:
        return ConnectionTestResult(key=key, success=False, message=f"Test failed: {str(e)}")
