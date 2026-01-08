"""
File-based encrypted settings storage.

Stores API keys and settings in an encrypted JSON file.
No database required - uses local filesystem.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.security.encryption import encrypt_value, decrypt_value, mask_secret


# Default settings file location
SETTINGS_DIR = Path(os.getenv("SETTINGS_DIR", ".settings"))
SETTINGS_FILE = SETTINGS_DIR / "config.enc.json"


# Default settings schema
DEFAULT_SETTINGS = {
    # LLM Providers
    "openai_api_key": {
        "category": "llm",
        "display_name": "OpenAI API Key",
        "description": "API key for OpenAI GPT models",
        "is_required": True,
        "is_secret": True,
        "value": "",
    },
    "anthropic_api_key": {
        "category": "llm",
        "display_name": "Anthropic API Key",
        "description": "API key for Anthropic Claude models",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    "llm_provider": {
        "category": "llm",
        "display_name": "Primary LLM Provider",
        "description": "Default LLM provider (openai or anthropic)",
        "is_required": True,
        "is_secret": False,
        "value": "openai",
    },
    
    # External APIs
    "congress_api_key": {
        "category": "external_api",
        "display_name": "Congress.gov API Key",
        "description": "API key for accessing Congress.gov data",
        "is_required": True,
        "is_secret": True,
        "value": "",
    },
    "twitter_bearer_token": {
        "category": "external_api",
        "display_name": "Twitter Bearer Token",
        "description": "Bearer token for Twitter/X API v2",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    "reddit_client_id": {
        "category": "external_api",
        "display_name": "Reddit Client ID",
        "description": "OAuth client ID for Reddit API",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    "reddit_client_secret": {
        "category": "external_api",
        "display_name": "Reddit Client Secret",
        "description": "OAuth client secret for Reddit API",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    "newsapi_key": {
        "category": "external_api",
        "display_name": "NewsAPI Key",
        "description": "API key for NewsAPI.org",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    
    # Communication
    "sendgrid_api_key": {
        "category": "communication",
        "display_name": "SendGrid API Key",
        "description": "API key for SendGrid email service",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    "sendgrid_from_email": {
        "category": "communication",
        "display_name": "SendGrid From Email",
        "description": "Verified sender email for SendGrid",
        "is_required": False,
        "is_secret": False,
        "value": "",
    },
    "twilio_account_sid": {
        "category": "communication",
        "display_name": "Twilio Account SID",
        "description": "Twilio account SID for SMS",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    "twilio_auth_token": {
        "category": "communication",
        "display_name": "Twilio Auth Token",
        "description": "Twilio auth token for SMS",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
    
    # Messaging
    "kafka_bootstrap_servers": {
        "category": "messaging",
        "display_name": "Kafka Bootstrap Servers",
        "description": "Comma-separated list of Kafka brokers",
        "is_required": False,
        "is_secret": False,
        "value": "",
    },
    "redis_dsn": {
        "category": "messaging",
        "display_name": "Redis Connection URL",
        "description": "Redis connection string for caching",
        "is_required": False,
        "is_secret": True,
        "value": "",
    },
}


class SettingsStore:
    """
    File-based encrypted settings store.
    
    Settings are stored in an encrypted JSON file.
    Thread-safe for reading, writes are atomic.
    """
    
    def __init__(self, settings_file: Optional[Path] = None):
        self.settings_file = settings_file or SETTINGS_FILE
        self._ensure_dir()
        self._settings: Dict[str, Any] = {}
        self._load()
    
    def _ensure_dir(self) -> None:
        """Ensure settings directory exists."""
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> None:
        """Load settings from file, initialize if not exists."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                self._settings = data.get("settings", {})
            except (json.JSONDecodeError, IOError):
                self._settings = {}
        
        # Merge with defaults (add any new settings)
        for key, default in DEFAULT_SETTINGS.items():
            if key not in self._settings:
                self._settings[key] = default.copy()
                self._settings[key]["updated_at"] = datetime.utcnow().isoformat()
        
        self._save()
    
    def _save(self) -> None:
        """Save settings to file atomically."""
        temp_file = self.settings_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump({
                    "version": 1,
                    "updated_at": datetime.utcnow().isoformat(),
                    "settings": self._settings,
                }, f, indent=2)
            temp_file.replace(self.settings_file)
        except IOError:
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all settings grouped by category."""
        categories: Dict[str, List[Dict[str, Any]]] = {}
        
        for key, setting in self._settings.items():
            cat = setting.get("category", "general")
            if cat not in categories:
                categories[cat] = []
            
            # Mask secret values for display
            value = setting.get("value", "")
            display_value = ""
            if value:
                if setting.get("is_secret", True):
                    try:
                        decrypted = decrypt_value(value)
                        display_value = mask_secret(decrypted)
                    except:
                        display_value = mask_secret(value)
                else:
                    display_value = value
            
            categories[cat].append({
                "id": key,
                "key": key,
                "category": cat,
                "display_name": setting.get("display_name", key),
                "description": setting.get("description", ""),
                "value": display_value,
                "is_secret": setting.get("is_secret", True),
                "is_configured": bool(value),
                "is_required": setting.get("is_required", False),
                "updated_at": setting.get("updated_at", datetime.utcnow().isoformat()),
            })
        
        return [
            {"category": cat, "settings": settings}
            for cat, settings in sorted(categories.items())
        ]
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a single setting by key."""
        return self._settings.get(key)
    
    def get_value(self, key: str) -> Optional[str]:
        """Get decrypted value for a setting. Used by agents."""
        setting = self._settings.get(key)
        if not setting:
            return None
        
        value = setting.get("value", "")
        if not value:
            # Fall back to environment variable
            env_key = key.upper()
            return os.getenv(env_key)
        
        if setting.get("is_secret", True):
            try:
                return decrypt_value(value)
            except:
                return value
        return value
    
    def set(self, key: str, value: str) -> bool:
        """Set a setting value. Encrypts secrets."""
        if key not in self._settings:
            return False
        
        setting = self._settings[key]
        
        if setting.get("is_secret", True) and value:
            setting["value"] = encrypt_value(value)
        else:
            setting["value"] = value
        
        setting["updated_at"] = datetime.utcnow().isoformat()
        self._save()
        return True
    
    def set_many(self, updates: Dict[str, str]) -> Dict[str, bool]:
        """Set multiple settings at once."""
        results = {}
        for key, value in updates.items():
            if value:  # Only update non-empty values
                results[key] = self.set(key, value)
            else:
                results[key] = True  # Skip empty values
        return results
    
    def clear(self, key: str) -> bool:
        """Clear a setting value."""
        if key not in self._settings:
            return False
        
        self._settings[key]["value"] = ""
        self._settings[key]["updated_at"] = datetime.utcnow().isoformat()
        self._save()
        return True


# Global instance
_store: Optional[SettingsStore] = None


def get_settings_store() -> SettingsStore:
    """Get the global settings store instance."""
    global _store
    if _store is None:
        _store = SettingsStore()
    return _store


def get_setting_value(key: str) -> Optional[str]:
    """
    Convenience function to get a decrypted setting value.
    Falls back to environment variable if not configured.
    
    Used by agents to retrieve API keys.
    """
    store = get_settings_store()
    value = store.get_value(key)
    
    if not value:
        # Fall back to environment variable
        return os.getenv(key.upper())
    
    return value
