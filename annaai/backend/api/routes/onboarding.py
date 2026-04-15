"""Onboarding routes — kick off site scrape + brand memory seeding."""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from agents.pipeline import run_onboarding_pipeline
from db.client import get_supabase_admin_client
from db.models import OnboardingStatusResponse
from dependencies import CurrentOrgUser, CurrentUser
from utils.logger import get_logger

logger = get_logger("onboarding")
router = APIRouter()

STEP_NAMES = ["website", "brand_voice", "connect_accounts", "goals"]


def _ensure_user_and_org(sb, user_id: str, email: str, org_name: str) -> str:
    """Create public.users + organizations rows on first onboarding if missing."""
    existing = sb.table("users").select("org_id").eq("id", user_id).execute()
    rows = existing.data or []
    if rows and rows[0].get("org_id"):
        return rows[0]["org_id"]

    org_res = (
        sb.table("organizations")
        .insert({"name": org_name or email.split("@")[0] or "My Org"})
        .execute()
    )
    org_id = (org_res.data or [{}])[0].get("id")
    if not org_id:
        raise HTTPException(500, "failed to create organization")

    sb.table("users").upsert(
        {"id": user_id, "email": email, "org_id": org_id, "role": "owner"}
    ).execute()
    return org_id


class OnboardRequest(BaseModel):
    website_url: HttpUrl
    name: str | None = Field(default=None, max_length=200)
    industry: str | None = None


class OnboardResponse(BaseModel):
    status: str
    message: str
    run_id: str | None = None


async def _run_onboarding_in_background(org_id: str, website_url: str) -> None:
    result = await run_onboarding_pipeline(org_id=org_id, website_url=website_url)
    logger.info("onboarding_finished", org_id=org_id, result_status=result.get("status"))


@router.post("", response_model=OnboardResponse)
async def start_onboarding(
    payload: OnboardRequest,
    background: BackgroundTasks,
    user: CurrentUser,
) -> OnboardResponse:
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")

    try:
        org_id = user.org_id or _ensure_user_and_org(
            sb, user.user_id, user.email, payload.name or ""
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"failed to provision org: {e}") from e

    updates = {"website_url": str(payload.website_url)}
    if payload.name:
        updates["name"] = payload.name
    if payload.industry:
        updates["industry"] = payload.industry
    try:
        sb.table("organizations").update(updates).eq("id", org_id).execute()
    except Exception as e:
        raise HTTPException(500, f"failed to save org: {e}") from e

    background.add_task(
        _run_onboarding_in_background, org_id, str(payload.website_url)
    )
    return OnboardResponse(
        status="started",
        message="Anna is scraping your site in the background. Check /onboarding/status.",
    )


@router.get("/status", response_model=OnboardingStatusResponse)
async def onboarding_status(user: CurrentUser) -> OnboardingStatusResponse:
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    if not user.org_id:
        return OnboardingStatusResponse(
            onboarding_complete=False,
            onboarding_step=0,
            total_steps=len(STEP_NAMES),
            current_step_name=STEP_NAMES[0],
        )
    try:
        res = (
            sb.table("organizations")
            .select("onboarding_complete,onboarding_step")
            .eq("id", user.org_id)
            .single()
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"status lookup failed: {e}") from e

    data = res.data or {}
    step = int(data.get("onboarding_step") or 0)
    return OnboardingStatusResponse(
        onboarding_complete=bool(data.get("onboarding_complete")),
        onboarding_step=step,
        total_steps=len(STEP_NAMES),
        current_step_name=STEP_NAMES[step] if 0 <= step < len(STEP_NAMES) else None,
    )
