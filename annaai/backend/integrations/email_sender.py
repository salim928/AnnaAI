"""Resend email integration — sends the daily brief."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import resend

from agents.prompts import BRIEF_EMAIL_HTML_TEMPLATE
from config import settings
from db.client import get_supabase_admin_client
from utils.logger import get_logger

logger = get_logger("email")


def _configure() -> bool:
    if not settings.RESEND_API_KEY:
        return False
    resend.api_key = settings.RESEND_API_KEY
    return True


def _recipient_for(org_id: str) -> str | None:
    sb = get_supabase_admin_client()
    if sb is None:
        return None
    try:
        res = (
            sb.table("organizations")
            .select("notification_email,name")
            .eq("id", org_id)
            .single()
            .execute()
        )
        return (res.data or {}).get("notification_email")
    except Exception as e:
        logger.warning("recipient_lookup_failed", error=str(e), org_id=org_id)
        return None


def send_email(*, to: str, subject: str, html: str) -> dict[str, Any]:
    if not _configure():
        logger.warning("resend_not_configured")
        return {"status": "skipped", "reason": "RESEND_API_KEY not set"}
    params = {
        "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
        "to": [to],
        "subject": subject,
        "html": html,
    }
    try:
        result = resend.Emails.send(params)
        logger.info("email_sent", to=to, subject=subject, id=result.get("id"))
        return {"status": "sent", "id": result.get("id")}
    except Exception as e:
        logger.error("email_send_failed", error=str(e))
        return {"status": "failed", "error": str(e)}


def render_daily_brief(
    *,
    brand_name: str,
    performance_summary: str,
    drafts: list[dict[str, Any]],
    key_insight: str,
    tomorrow_plan: str,
) -> str:
    date_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    if drafts:
        drafts_html = "".join(
            f"""
            <div style="border:1px solid #eeeef2;border-radius:8px;padding:14px;margin-bottom:12px;">
              <div style="font-size:13px;color:#888899;text-transform:uppercase;letter-spacing:0.04em;">
                {d.get('type','content').replace('_',' ')}
              </div>
              <div style="font-size:15px;font-weight:600;margin-top:4px;color:#1a1a2e;">
                {d.get('title','Untitled')}
              </div>
              <div style="margin-top:10px;">
                <a href="{settings.FRONTEND_URL}/drafts/{d.get('id','')}"
                   style="color:#e94560;font-size:13px;text-decoration:none;">
                  Review & approve →
                </a>
              </div>
            </div>
            """.strip()
            for d in drafts
        )
    else:
        drafts_html = (
            '<p style="margin:0;font-size:14px;color:#666677;">'
            "No drafts today — Anna is tuning the plan for tomorrow.</p>"
        )

    return BRIEF_EMAIL_HTML_TEMPLATE.format(
        date_str=date_str,
        brand_name=brand_name,
        performance_summary=performance_summary,
        drafts_html=drafts_html,
        key_insight=key_insight,
        tomorrow_plan=tomorrow_plan,
        dashboard_url=f"{settings.FRONTEND_URL}/dashboard",
        unsubscribe_url=f"{settings.FRONTEND_URL}/settings",
    )


def send_daily_brief(*, org_id: str, subject: str, html_body: str) -> str:
    to = _recipient_for(org_id)
    if not to:
        return "no recipient on file — set notification_email in settings"
    result = send_email(to=to, subject=subject, html=html_body)

    sb = get_supabase_admin_client()
    if sb is not None:
        try:
            sb.table("daily_briefs").insert(
                {
                    "org_id": org_id,
                    "subject": subject,
                    "html_body": html_body,
                    "sent_to": to,
                }
            ).execute()
        except Exception as e:
            logger.warning("daily_brief_log_failed", error=str(e))

    return f"brief sent: {result.get('status')}"
