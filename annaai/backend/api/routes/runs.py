"""Agent runs — list, stats, trigger."""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request

from agents.pipeline import _count_runs_today, _max_runs_per_day, run_daily_pipeline_for_org
from api.rate_limit import limiter
from db.client import get_supabase_admin_client
from db.models import AgentRunResponse, PaginatedResponse, RunStatsResponse
from dependencies import CurrentOrgUser
from utils.logger import get_logger

logger = get_logger("runs")
router = APIRouter()


@router.get("", response_model=PaginatedResponse[AgentRunResponse])
async def list_runs(
    user: CurrentOrgUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[AgentRunResponse]:
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")

    start = (page - 1) * page_size
    end = start + page_size - 1
    try:
        res = (
            sb.table("agent_runs")
            .select("*", count="exact")
            .eq("org_id", user.org_id)
            .order("started_at", desc=True)
            .range(start, end)
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"runs query failed: {e}") from e

    items = [AgentRunResponse.model_validate(row) for row in (res.data or [])]
    total = int(res.count or 0)
    return PaginatedResponse[AgentRunResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(start + len(items)) < total,
    )


@router.get("/stats", response_model=RunStatsResponse)
async def run_stats(user: CurrentOrgUser) -> RunStatsResponse:
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    try:
        res = sb.rpc("get_org_run_stats", {"p_org_id": user.org_id}).execute()
    except Exception as e:
        raise HTTPException(500, f"stats query failed: {e}") from e

    row = (res.data or [{}])[0] if isinstance(res.data, list) else (res.data or {})
    return RunStatsResponse(
        total_runs=int(row.get("total_runs") or 0),
        successful_runs=int(row.get("successful_runs") or 0),
        failed_runs=int(row.get("failed_runs") or 0),
        total_drafts=int(row.get("total_drafts") or 0),
        published_drafts=int(row.get("published_drafts") or 0),
        avg_duration_seconds=float(row.get("avg_duration_seconds") or 0.0),
    )


@router.post("/trigger")
@limiter.limit("5/minute")
async def trigger_run(request: Request, background: BackgroundTasks, user: CurrentOrgUser) -> dict[str, str]:
    # Pre-check plan limits before queuing so the user gets immediate feedback
    sb = get_supabase_admin_client()
    plan = "free"
    if sb:
        try:
            res = sb.table("organizations").select("plan").eq("id", user.org_id).single().execute()
            plan = (res.data or {}).get("plan", "free")
        except Exception:
            pass

    runs_today = await _count_runs_today(user.org_id or "")
    max_runs = _max_runs_per_day(plan)
    if runs_today >= max_runs:
        raise HTTPException(
            429,
            f"Daily run limit reached ({max_runs} runs/day on {plan} plan). Upgrade for more.",
        )

    async def _go() -> None:
        await run_daily_pipeline_for_org(user.org_id or "")

    background.add_task(_go)
    return {"status": "queued", "message": "Anna is running now. Refresh runs in a moment."}
