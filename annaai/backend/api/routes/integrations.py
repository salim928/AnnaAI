"""Integration routes — WordPress connect + Google OAuth stub."""
from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, HttpUrl

from config import settings
from db.client import get_supabase_admin_client
from dependencies import CurrentOrgUser
from integrations.wordpress import save_credentials as save_wp
from utils.encryption import encrypt_token
from utils.logger import get_logger

logger = get_logger("integrations")
router = APIRouter()


# --- Listing ---------------------------------------------------------------
@router.get("")
async def list_integrations(user: CurrentOrgUser) -> dict[str, list[dict]]:
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    try:
        res = (
            sb.table("oauth_tokens")
            .select("platform,metadata,expires_at,created_at")
            .eq("org_id", user.org_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"integrations query failed: {e}") from e

    connected = [
        {
            "platform": row["platform"],
            "metadata": row.get("metadata") or {},
            "expires_at": row.get("expires_at"),
            "connected_at": row.get("created_at"),
        }
        for row in (res.data or [])
    ]
    return {"connected": connected}


# --- WordPress -------------------------------------------------------------
class WordPressConnectRequest(BaseModel):
    wp_url: HttpUrl
    wp_username: str = Field(..., min_length=1, max_length=200)
    wp_app_password: str = Field(..., min_length=1, max_length=400)


@router.post("/wordpress/connect")
async def connect_wordpress(
    payload: WordPressConnectRequest,
    user: CurrentOrgUser,
) -> dict[str, str]:
    result = save_wp(
        org_id=user.org_id or "",
        wp_url=str(payload.wp_url),
        wp_username=payload.wp_username,
        wp_app_password=payload.wp_app_password,
    )
    if result.get("status") != "connected":
        raise HTTPException(500, result.get("error") or "wordpress connect failed")
    return {"status": "connected", "wp_url": result["wp_url"]}


# --- Google OAuth (start + callback) --------------------------------------
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
    "openid",
    "email",
    "profile",
]


@router.get("/google/authorize")
async def google_authorize(user: CurrentOrgUser) -> dict[str, str]:
    if not (settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET):
        raise HTTPException(503, "Google OAuth is not configured")
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.BACKEND_URL}/api/integrations/google/callback",
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": user.org_id or "",
    }
    return {"authorize_url": f"{GOOGLE_AUTH_URL}?{urlencode(params)}"}


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
) -> dict[str, str]:
    if not (settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET):
        raise HTTPException(503, "Google OAuth is not configured")

    import httpx

    try:
        resp = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.BACKEND_URL}/api/integrations/google/callback",
                "grant_type": "authorization_code",
            },
            timeout=30,
        )
        resp.raise_for_status()
        tokens = resp.json()
    except Exception as e:
        raise HTTPException(400, f"token exchange failed: {e}") from e

    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")

    row = {
        "org_id": state,
        "platform": "google",
        "access_token": encrypt_token(tokens.get("access_token", "")),
        "refresh_token": encrypt_token(tokens.get("refresh_token", "")),
        "scope": tokens.get("scope"),
        "metadata": {},
    }
    try:
        sb.table("oauth_tokens").upsert(row, on_conflict="org_id,platform").execute()
    except Exception as e:
        raise HTTPException(500, f"token store failed: {e}") from e

    return {"status": "connected", "platform": "google"}


@router.delete("/{platform}")
async def disconnect(platform: str, user: CurrentOrgUser) -> dict[str, str]:
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    try:
        sb.table("oauth_tokens").delete().eq("org_id", user.org_id).eq(
            "platform", platform
        ).execute()
    except Exception as e:
        raise HTTPException(500, f"disconnect failed: {e}") from e
    return {"status": "disconnected", "platform": platform}
