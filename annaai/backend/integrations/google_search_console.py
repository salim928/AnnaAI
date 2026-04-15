"""Google Search Console — top-keyword fetcher."""
from __future__ import annotations

from datetime import datetime, timedelta

import httpx

from db.client import get_supabase_admin_client
from utils.encryption import decrypt_token
from utils.logger import get_logger

logger = get_logger("gsc")

GSC_BASE = "https://searchconsole.googleapis.com/webmasters/v3/sites"


def _load(org_id: str) -> dict[str, str] | None:
    sb = get_supabase_admin_client()
    if sb is None:
        return None
    try:
        res = (
            sb.table("oauth_tokens")
            .select("access_token,metadata")
            .eq("org_id", org_id)
            .eq("platform", "google")
            .single()
            .execute()
        )
        data = res.data or {}
    except Exception as e:
        logger.warning("gsc_token_lookup_failed", error=str(e))
        return None

    access = decrypt_token(data.get("access_token") or "")
    site_url = (data.get("metadata") or {}).get("gsc_site_url")
    if not (access and site_url):
        return None
    return {"access_token": access, "site_url": site_url}


def fetch_top_keywords(*, org_id: str, days: int = 30) -> str:
    creds = _load(org_id)
    if creds is None:
        return "Google Search Console not connected."

    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    body = {
        "startDate": str(start),
        "endDate": str(end),
        "dimensions": ["query"],
        "rowLimit": 10,
    }
    url = f"{GSC_BASE}/{httpx.QueryParams({'site': creds['site_url']})['site']}/searchAnalytics/query"
    # The GSC endpoint expects the site URL URL-encoded in the path directly.
    import urllib.parse

    url = f"{GSC_BASE}/{urllib.parse.quote(creds['site_url'], safe='')}/searchAnalytics/query"

    try:
        resp = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {creds['access_token']}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        rows = resp.json().get("rows", [])
    except Exception as e:
        logger.warning("gsc_report_failed", error=str(e))
        return f"GSC report failed: {e}"

    if not rows:
        return "No search console data in the window."
    lines = [f"Search Console — top keywords ({days}d):"]
    for row in rows:
        kw = (row.get("keys") or [""])[0]
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        lines.append(f"- {kw}: {clicks} clicks, {impressions} impressions")
    return "\n".join(lines)
