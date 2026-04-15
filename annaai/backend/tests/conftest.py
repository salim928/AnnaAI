"""Shared pytest fixtures for AnnaAi backend tests."""
from __future__ import annotations

import asyncio
import os
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ENCRYPTION_KEY", "CnoL2u8A5q9f0xH7iHkQ2WnT5P1lJvRkB9YgwYoF8gM=")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service")


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def client() -> Iterator[TestClient]:
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def fake_org_id() -> str:
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture()
def fake_user() -> dict[str, Any]:
    return {
        "id": "00000000-0000-0000-0000-00000000aaaa",
        "email": "test@annaai.app",
        "org_id": "00000000-0000-0000-0000-000000000001",
    }
