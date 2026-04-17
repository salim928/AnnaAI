"""Organization settings — profile, brand voice, notifications, account deletion."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from api.rate_limit import limiter
from db.client import get_supabase_admin_client
from db.models import OrgResponse, OrgUpdate
from dependencies import CurrentOrgUser, CurrentUser
from utils.logger import get_logger

logger = get_logger("settings")
router = APIRouter()


@router.get("", response_model=OrgResponse)
async def get_settings(user: CurrentOrgUser) -> OrgResponse:
    """Return the full org profile for the settings page."""
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    try:
        res = (
            sb.table("organizations")
            .select("*")
            .eq("id", user.org_id)
            .single()
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"settings fetch failed: {e}") from e

    if not res.data:
        raise HTTPException(404, "organization not found")
    return OrgResponse.model_validate(res.data)


@router.patch("", response_model=OrgResponse)
@limiter.limit("10/minute")
async def update_settings(
    request: Request,
    body: OrgUpdate,
    user: CurrentOrgUser,
) -> OrgResponse:
    """Update org profile fields. Only non-null fields are written."""
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(400, "no fields to update")

    # Convert HttpUrl to string for DB storage
    if "website_url" in updates:
        updates["website_url"] = str(updates["website_url"])

    try:
        res = (
            sb.table("organizations")
            .update(updates)
            .eq("id", user.org_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"settings update failed: {e}") from e

    row = (res.data or [{}])[0]
    if not row:
        raise HTTPException(404, "organization not found")

    logger.info("settings_updated", org_id=user.org_id, fields=list(updates.keys()))
    return OrgResponse.model_validate(row)


@router.delete("/account")
@limiter.limit("2/minute")
async def delete_account(request: Request, user: CurrentUser) -> dict[str, str]:
    """Delete the user's account and all associated org data.

    Because all tables use ON DELETE CASCADE from organizations, deleting
    the org row removes runs, drafts, brand_memory, chat_messages, etc.
    The Supabase auth user is also deleted via the admin API.
    """
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")

    org_id = user.org_id

    try:
        # 1. Delete org (cascades to all child tables)
        if org_id:
            sb.table("organizations").delete().eq("id", org_id).execute()
            logger.info("org_deleted", org_id=org_id, user_id=user.user_id)

        # 2. Delete the user row from public.users
        sb.table("users").delete().eq("id", user.user_id).execute()

        # 3. Delete the Supabase auth user
        sb.auth.admin.delete_user(user.user_id)
        logger.info("auth_user_deleted", user_id=user.user_id)

    except Exception as e:
        logger.error("account_deletion_failed", user_id=user.user_id, error=str(e))
        raise HTTPException(500, f"account deletion failed: {e}") from e

    return {"status": "deleted"}
