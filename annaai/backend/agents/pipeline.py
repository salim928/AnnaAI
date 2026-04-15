"""Async orchestration around CrewAI — daily pipeline + onboarding pipeline.

CrewAI's `kickoff()` is synchronous, so we run it in a thread pool via
`asyncio.to_thread` to avoid blocking the FastAPI event loop.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any
from uuid import UUID

from agents.crew import AnnaCrew, AnnaCrewConfig
from agents.tools import set_agent_context
from db.client import get_supabase_admin_client
from memory.scraper import scrape_site
from memory.vector_store import store_brand_memory
from utils.helpers import extract_domain
from utils.logger import (
    get_logger,
    log_agent_run_complete,
    log_agent_run_failed,
    log_agent_run_start,
)

logger = get_logger("pipeline")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _create_run(org_id: str, run_type: str) -> str | None:
    sb = get_supabase_admin_client()
    if sb is None:
        return None
    try:
        res = await asyncio.to_thread(
            lambda: sb.table("agent_runs")
            .insert({"org_id": org_id, "status": "running", "run_type": run_type})
            .execute()
        )
        return (res.data or [{}])[0].get("id")
    except Exception as e:
        logger.warning("create_run_failed", error=str(e))
        return None


async def _complete_run(
    run_id: str,
    *,
    status: str,
    summary: str | None = None,
    error_message: str | None = None,
) -> None:
    sb = get_supabase_admin_client()
    if sb is None or not run_id:
        return
    try:
        await asyncio.to_thread(
            lambda: sb.table("agent_runs")
            .update(
                {
                    "status": status,
                    "summary": summary,
                    "error_message": error_message,
                    "completed_at": "now()",
                }
            )
            .eq("id", run_id)
            .execute()
        )
    except Exception as e:
        logger.warning("complete_run_failed", error=str(e), run_id=run_id)


async def _load_org(org_id: str) -> dict[str, Any] | None:
    sb = get_supabase_admin_client()
    if sb is None:
        return None
    try:
        res = await asyncio.to_thread(
            lambda: sb.table("organizations").select("*").eq("id", org_id).single().execute()
        )
        return res.data
    except Exception as e:
        logger.warning("load_org_failed", error=str(e), org_id=org_id)
        return None


async def _list_active_orgs() -> list[dict[str, Any]]:
    sb = get_supabase_admin_client()
    if sb is None:
        return []
    try:
        res = await asyncio.to_thread(
            lambda: sb.table("organizations")
            .select("id, name, industry, plan, onboarding_complete")
            .eq("onboarding_complete", True)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.warning("list_orgs_failed", error=str(e))
        return []


# ---------------------------------------------------------------------------
# Onboarding pipeline
# ---------------------------------------------------------------------------
async def run_onboarding_pipeline(
    org_id: str,
    website_url: str,
) -> dict[str, Any]:
    """Scrape the user's site and seed brand memory. No crew kickoff yet."""
    try:
        UUID(org_id)
    except ValueError:
        return {"status": "error", "error": "invalid org_id"}

    run_id = await _create_run(org_id, run_type="onboarding")
    log_agent_run_start(org_id, run_id or "local", "onboarding")
    started = time.perf_counter()

    try:
        scrape = await scrape_site(website_url)
        if not scrape.pages:
            raise RuntimeError("scraper returned no pages")

        stored = await asyncio.to_thread(store_brand_memory, org_id, scrape)

        sb = get_supabase_admin_client()
        if sb is not None:
            await asyncio.to_thread(
                lambda: sb.table("organizations")
                .update(
                    {
                        "onboarding_complete": True,
                        "onboarding_step": 4,
                        "website_url": website_url,
                    }
                )
                .eq("id", org_id)
                .execute()
            )

        duration = time.perf_counter() - started
        summary = f"Onboarded {scrape.domain}: {len(scrape.pages)} pages, {stored} chunks"
        if run_id:
            await _complete_run(run_id, status="completed", summary=summary)
        log_agent_run_complete(org_id, run_id or "local", duration, drafts_created=0)
        return {
            "status": "completed",
            "run_id": run_id,
            "pages": len(scrape.pages),
            "chunks": stored,
            "domain": scrape.domain,
            "duration_seconds": round(duration, 2),
        }
    except Exception as e:
        log_agent_run_failed(org_id, run_id or "local", str(e))
        if run_id:
            await _complete_run(run_id, status="failed", error_message=str(e))
        return {"status": "failed", "error": str(e)}


# ---------------------------------------------------------------------------
# Daily pipeline — single org
# ---------------------------------------------------------------------------
async def run_daily_pipeline_for_org(org_id: str) -> dict[str, Any]:
    try:
        UUID(org_id)
    except ValueError:
        return {"status": "error", "error": "invalid org_id"}

    org = await _load_org(org_id)
    if org is None:
        return {"status": "error", "error": "org not found or supabase not configured"}
    if not org.get("onboarding_complete"):
        return {"status": "skipped", "reason": "onboarding incomplete"}

    run_id = await _create_run(org_id, run_type="daily")
    log_agent_run_start(org_id, run_id or "local", "daily")
    started = time.perf_counter()

    brand_name = org.get("name") or extract_domain(org.get("website_url") or "") or "your brand"
    industry = org.get("industry") or "technology"
    plan = org.get("plan") or "free"

    try:
        set_agent_context(org_id=org_id, run_id=run_id)
        crew = AnnaCrew(
            AnnaCrewConfig(
                org_id=org_id,
                brand_name=brand_name,
                industry=industry,
                plan=plan,
                run_type="daily",
            )
        )
        result = await asyncio.to_thread(crew.crew().kickoff)
        duration = time.perf_counter() - started
        summary = str(result)[:1200]
        if run_id:
            await _complete_run(run_id, status="completed", summary=summary)
        log_agent_run_complete(org_id, run_id or "local", duration, drafts_created=1)
        return {
            "status": "completed",
            "run_id": run_id,
            "summary": summary,
            "duration_seconds": round(duration, 2),
        }
    except Exception as e:
        log_agent_run_failed(org_id, run_id or "local", str(e))
        if run_id:
            await _complete_run(run_id, status="failed", error_message=str(e))
        return {"status": "failed", "error": str(e), "run_id": run_id}


# ---------------------------------------------------------------------------
# Daily pipeline — every active org
# ---------------------------------------------------------------------------
async def run_daily_pipeline_for_all_orgs() -> dict[str, Any]:
    orgs = await _list_active_orgs()
    if not orgs:
        return {"status": "completed", "orgs": 0, "results": []}

    results: list[dict[str, Any]] = []
    for org in orgs:
        res = await run_daily_pipeline_for_org(org["id"])
        results.append({"org_id": org["id"], "name": org.get("name"), **res})
    success = sum(1 for r in results if r.get("status") == "completed")
    return {"status": "completed", "orgs": len(orgs), "success": success, "results": results}
