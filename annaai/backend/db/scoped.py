"""Multi-tenant scoped client helpers.

Forces every query to filter by `org_id` so cross-tenant leaks are a type
error, not a runtime surprise. Use this in any code path that runs outside
an RLS-aware user session (Celery tasks, agent tools, webhook handlers).
"""
from __future__ import annotations

from typing import Any

from db.client import require_admin_client


class OrgScopedClient:
    """Tiny wrapper that auto-scopes `table(...)` queries to one organization."""

    _SCOPED_TABLES = {
        "agent_runs",
        "content_drafts",
        "daily_briefs",
        "chat_messages",
        "scheduled_tasks",
        "brand_memory",
        "oauth_tokens",
    }

    def __init__(self, org_id: str) -> None:
        if not org_id:
            raise ValueError("org_id is required")
        self.org_id = org_id
        self._sb = require_admin_client()

    def table(self, name: str):
        query = self._sb.table(name)
        if name in self._SCOPED_TABLES:
            query = query.eq("org_id", self.org_id)
        return query

    def insert(self, name: str, row: dict[str, Any]):
        if name in self._SCOPED_TABLES:
            row = {**row, "org_id": self.org_id}
        return self._sb.table(name).insert(row).execute()

    def upsert(self, name: str, row: dict[str, Any], on_conflict: str | None = None):
        if name in self._SCOPED_TABLES:
            row = {**row, "org_id": self.org_id}
        q = self._sb.table(name).upsert(row, on_conflict=on_conflict or "")
        return q.execute()

    @property
    def raw(self):
        """Escape hatch for the unscoped admin client."""
        return self._sb
