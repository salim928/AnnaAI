"""Scheduler endpoint — called by GitHub Actions cron."""
from __future__ import annotations

import hmac

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from agents.pipeline import run_daily_pipeline_for_all_orgs
from api.rate_limit import SCHEDULER_LIMIT, limiter
from config import settings
from utils.logger import get_logger

logger = get_logger("scheduler")
router = APIRouter()


def _require_scheduler_auth(authorization: str | None) -> None:
    if not settings.SCHEDULER_SECRET:
        # Dev convenience: no secret means the endpoint is open locally.
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "missing bearer token")
    token = authorization.split(" ", 1)[1]
    if not hmac.compare_digest(token, settings.SCHEDULER_SECRET):
        raise HTTPException(401, "invalid scheduler token")


@router.post("/trigger-all-runs")
@limiter.limit(SCHEDULER_LIMIT)
async def trigger_all_runs(
    request: Request,
    background: BackgroundTasks,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    _require_scheduler_auth(authorization)

    async def _go() -> None:
        result = await run_daily_pipeline_for_all_orgs()
        logger.info("scheduler_trigger_done", **result)

    background.add_task(_go)
    return {"status": "accepted", "message": "daily runs queued"}
