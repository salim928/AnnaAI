"""WordPress REST API integration — async httpx + application-password auth."""
from __future__ import annotations

import base64
from typing import Any

import httpx

from db.client import get_supabase_admin_client
from utils.encryption import decrypt_token
from utils.logger import get_logger

logger = get_logger("wordpress")


def _load_credentials(org_id: str) -> dict[str, str] | None:
    sb = get_supabase_admin_client()
    if sb is None:
        return None
    try:
        res = (
            sb.table("oauth_tokens")
            .select("metadata,access_token")
            .eq("org_id", org_id)
            .eq("platform", "wordpress")
            .single()
            .execute()
        )
        data = res.data or {}
    except Exception as e:
        logger.warning("wp_creds_lookup_failed", error=str(e))
        return None

    metadata = data.get("metadata") or {}
    wp_url = metadata.get("wp_url")
    wp_user = metadata.get("wp_username")
    app_password = decrypt_token(data.get("access_token") or "") or ""
    if not (wp_url and wp_user and app_password):
        return None
    return {"url": wp_url.rstrip("/"), "user": wp_user, "password": app_password}


def _auth_header(user: str, password: str) -> str:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {token}"


def list_recent_posts(*, org_id: str, limit: int = 5) -> str:
    creds = _load_credentials(org_id)
    if creds is None:
        return "WordPress not connected — connect it from Integrations."
    url = f"{creds['url']}/wp-json/wp/v2/posts"
    try:
        resp = httpx.get(
            url,
            params={"per_page": limit, "_fields": "id,title,link,date"},
            headers={"Authorization": _auth_header(creds["user"], creds["password"])},
            timeout=20,
        )
        resp.raise_for_status()
        posts = resp.json()
    except Exception as e:
        return f"WordPress fetch failed: {e}"
    if not posts:
        return "No recent posts found."
    return "\n".join(
        f"- {p.get('title', {}).get('rendered', 'Untitled')} ({p.get('link', '')})" for p in posts
    )


def create_post(
    *,
    org_id: str,
    title: str,
    content: str,
    status: str = "draft",
) -> str:
    creds = _load_credentials(org_id)
    if creds is None:
        return "WordPress not connected."
    url = f"{creds['url']}/wp-json/wp/v2/posts"
    payload: dict[str, Any] = {"title": title, "content": content, "status": status}
    try:
        resp = httpx.post(
            url,
            json=payload,
            headers={"Authorization": _auth_header(creds["user"], creds["password"])},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        link = data.get("link") or data.get("guid", {}).get("rendered", "")
        logger.info("wp_post_created", id=data.get("id"), link=link, status=status)
        return f"created: id={data.get('id')} status={status} url={link}"
    except Exception as e:
        logger.error("wp_post_create_failed", error=str(e))
        return f"publish failed: {e}"


def save_credentials(
    *,
    org_id: str,
    wp_url: str,
    wp_username: str,
    wp_app_password: str,
) -> dict[str, Any]:
    """Store WP creds in oauth_tokens (the app-password is Fernet-encrypted)."""
    from utils.encryption import encrypt_token

    sb = get_supabase_admin_client()
    if sb is None:
        return {"status": "error", "error": "supabase not configured"}

    row = {
        "org_id": org_id,
        "platform": "wordpress",
        "access_token": encrypt_token(wp_app_password),
        "refresh_token": None,
        "metadata": {"wp_url": wp_url.rstrip("/"), "wp_username": wp_username},
    }
    try:
        sb.table("oauth_tokens").upsert(row, on_conflict="org_id,platform").execute()
    except Exception as e:
        return {"status": "error", "error": str(e)}
    return {"status": "connected", "wp_url": wp_url}
