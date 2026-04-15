"""Supabase client helpers — supabase-py v2."""
from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from config import settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client | None:
    """Anon-key client. Honours RLS. Safe for user-scoped reads."""
    if not (settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY):
        return None
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@lru_cache(maxsize=1)
def get_supabase_admin_client() -> Client | None:
    """Service-role client. Bypasses RLS. Server-only."""
    if not (settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY):
        return None
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def require_admin_client() -> Client:
    client = get_supabase_admin_client()
    if client is None:
        raise RuntimeError(
            "Supabase admin client is not configured — "
            "set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )
    return client
