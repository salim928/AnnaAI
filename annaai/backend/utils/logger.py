"""Structured logging via structlog. JSON in production, pretty console in dev."""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from config import settings

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return

    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.is_production:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    configure_logging()
    return structlog.get_logger(name or "annaai")


def log_agent_run_start(org_id: str, run_id: str, run_type: str) -> None:
    get_logger("agents").info(
        "agent_run_start", org_id=org_id, run_id=run_id, run_type=run_type
    )


def log_agent_run_complete(
    org_id: str, run_id: str, duration_seconds: float, drafts_created: int
) -> None:
    get_logger("agents").info(
        "agent_run_complete",
        org_id=org_id,
        run_id=run_id,
        duration_seconds=round(duration_seconds, 2),
        drafts_created=drafts_created,
    )


def log_agent_run_failed(org_id: str, run_id: str, error: str) -> None:
    get_logger("agents").error(
        "agent_run_failed", org_id=org_id, run_id=run_id, error=error
    )


def log_api_request(method: str, path: str, status: int, duration_ms: float, **extra: Any) -> None:
    get_logger("api").info(
        "api_request",
        method=method,
        path=path,
        status=status,
        duration_ms=round(duration_ms, 2),
        **extra,
    )
