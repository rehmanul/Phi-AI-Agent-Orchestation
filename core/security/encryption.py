"""
Encryption utilities for secure storage of API keys and secrets.
Uses Fernet symmetric encryption with key derived from API_SECRET_KEY.
"""

import base64
import hashlib
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


def get_encryption_key() -> bytes:
    """
    Derive a Fernet-compatible encryption key from API_SECRET_KEY.
    Falls back to a default for development only.
    """
    secret = os.getenv("API_SECRET_KEY", "")
    
    if not secret:
        # In production, API_SECRET_KEY must be set
        raise ValueError("API_SECRET_KEY environment variable is required for encryption")
    
    # Derive a 32-byte key using SHA-256
    key_bytes = hashlib.sha256(secret.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string and return base64-encoded ciphertext.
    
    Args:
        plaintext: The secret value to encrypt
        
    Returns:
        Base64-encoded encrypted string
    """
    if not plaintext:
        return ""
    
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plaintext.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_value(ciphertext: str) -> str:
    """
    Decrypt a base64-encoded ciphertext string.
    
    Args:
        ciphertext: The encrypted value
        
    Returns:
        Decrypted plaintext string
        
    Raises:
        InvalidToken: If decryption fails (wrong key or corrupted data)
    """
    if not ciphertext:
        return ""
    
    key = get_encryption_key()
    fernet = Fernet(key)
    
    try:
        decrypted = fernet.decrypt(ciphertext.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        raise ValueError("Failed to decrypt value - key may have changed or data is corrupted")


def mask_secret(value: str, visible_chars: int = 4) -> str:
    """
    Mask a secret value for display purposes.
    Shows first N characters followed by asterisks.
    
    Args:
        value: The secret value to mask
        visible_chars: Number of characters to show at the start
        
    Returns:
        Masked string like "sk-a***"
    """
    if not value:
        return ""
    
    if len(value) <= visible_chars:
        return "*" * len(value)
    
    return value[:visible_chars] + "*" * min(8, len(value) - visible_chars)


def is_valid_api_key(key_type: str, value: str) -> bool:
    """
    Basic validation for API key format.
    
    Args:
        key_type: The type of API key (openai, anthropic, etc.)
        value: The key value to validate
        
    Returns:
        True if the format looks valid
    """
    if not value:
        return False
    
    validations = {
        "openai_api_key": lambda k: k.startswith("sk-") and len(k) > 20,
        "anthropic_api_key": lambda k: k.startswith("sk-ant-") and len(k) > 20,
        "sendgrid_api_key": lambda k: k.startswith("SG.") and len(k) > 20,
        "congress_api_key": lambda k: len(k) > 10,
        "twitter_bearer_token": lambda k: len(k) > 50,
        "newsapi_key": lambda k: len(k) >= 32,
    }
    
    validator = validations.get(key_type, lambda k: len(k) > 5)
    return validator(value)
