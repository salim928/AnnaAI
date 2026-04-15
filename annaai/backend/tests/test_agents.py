"""Unit tests for agent helpers, memory, and utilities."""
from __future__ import annotations

import pytest

from utils.encryption import decrypt_token, encrypt_token, verify_webhook_signature
from utils.helpers import (
    chunk_text,
    clean_html,
    extract_domain,
    format_duration,
    generate_slug,
    truncate_text,
)


def test_chunk_text_splits_on_boundaries() -> None:
    text = "abc. def. ghi. jkl."
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) > 1
    assert all(len(c) <= 12 for c in chunks)


def test_clean_html_strips_tags() -> None:
    html = "<p>Hello <b>world</b></p><script>evil()</script>"
    cleaned = clean_html(html)
    assert "evil()" not in cleaned
    assert "Hello" in cleaned
    assert "world" in cleaned


def test_extract_domain() -> None:
    assert extract_domain("https://www.example.com/path?x=1") == "example.com"
    assert extract_domain("http://blog.example.co.uk") == "blog.example.co.uk"


def test_generate_slug() -> None:
    assert generate_slug("Hello, World!") == "hello-world"
    assert generate_slug("  Leading & Trailing  ") == "leading-trailing"


def test_truncate_text() -> None:
    assert truncate_text("abcdefghij", 5) == "abcd…"
    assert truncate_text("short", 20) == "short"


def test_format_duration() -> None:
    assert format_duration(45) == "45s"
    assert "m" in format_duration(120)
    assert "h" in format_duration(7200)


def test_encrypt_decrypt_round_trip() -> None:
    token = "super-secret-token-123"
    ciphertext = encrypt_token(token)
    assert ciphertext != token
    assert decrypt_token(ciphertext) == token


def test_verify_webhook_signature_matches() -> None:
    import hashlib
    import hmac

    secret = "test-secret"
    body = b'{"event":"x"}'
    sig = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
    assert verify_webhook_signature(body, sig, secret) is True
    assert verify_webhook_signature(body, "bogus", secret) is False


@pytest.mark.asyncio
async def test_embedding_service_singleton() -> None:
    pytest.importorskip("sentence_transformers")
    from memory.embedder import EmbeddingService

    svc1 = EmbeddingService()
    svc2 = EmbeddingService()
    assert svc1 is svc2
