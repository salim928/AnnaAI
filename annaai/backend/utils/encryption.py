"""Symmetric encryption for OAuth tokens + webhook signature verification."""
from __future__ import annotations

import hashlib
import hmac
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _fernet() -> Fernet | None:
    if not settings.ENCRYPTION_KEY:
        return None
    try:
        return Fernet(settings.ENCRYPTION_KEY.encode())
    except Exception as e:
        logger.error("fernet_init_failed", error=str(e))
        return None


def encrypt_token(plaintext: str) -> str:
    """Encrypt a secret. Returns ciphertext. Falls through plaintext when key missing."""
    if not plaintext:
        return plaintext
    f = _fernet()
    if f is None:
        logger.warning("encryption_key_missing_storing_plaintext")
        return plaintext
    return f.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str | None:
    if not ciphertext:
        return None
    f = _fernet()
    if f is None:
        return ciphertext
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        logger.error("token_decrypt_failed")
        return None


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """HMAC-SHA256 constant-time comparison for webhook payloads."""
    if not (signature and secret):
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
