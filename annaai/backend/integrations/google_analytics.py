"""Google Analytics Data API (GA4) — minimal read-only client."""
from __future__ import annotations

from datetime import datetime, timedelta

from db.client import get_supabase_admin_client
from utils.encryption import decrypt_token
from utils.logger import get_logger

logger = get_logger("ga4")


def _load_tokens(org_id: str) -> dict[str, str] | None:
    sb = get_supabase_admin_client()
    if sb is None:
        return None
    try:
        res = (
            sb.table("oauth_tokens")
            .select("access_token,refresh_token,metadata,expires_at")
            .eq("org_id", org_id)
            .eq("platform", "google")
            .single()
            .execute()
        )
        data = res.data or {}
    except Exception as e:
        logger.warning("ga_token_lookup_failed", error=str(e))
        return None

    access = decrypt_token(data.get("access_token") or "")
    refresh = decrypt_token(data.get("refresh_token") or "")
    metadata = data.get("metadata") or {}
    property_id = metadata.get("ga_property_id")
    if not (access and property_id):
        return None
    return {
        "access_token": access,
        "refresh_token": refresh or "",
        "property_id": property_id,
    }


def fetch_top_pages(*, org_id: str, days: int = 30, limit: int = 50) -> list[dict]:
    """Structured top-pages list for the feedback-loop task. Returns []
    when GA is not connected or fails — callers should treat that as a skip.
    """
    tokens = _load_tokens(org_id)
    if tokens is None:
        return []

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        from google.oauth2.credentials import Credentials
    except Exception:  # noqa: BLE001
        return []

    creds = Credentials(
        token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token") or None,
    )

    try:
        client = BetaAnalyticsDataClient(credentials=creds)
        end = datetime.utcnow().date()
        start = end - timedelta(days=days)
        request = RunReportRequest(
            property=f"properties/{tokens['property_id']}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
            ],
            date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
            limit=limit,
        )
        response = client.run_report(request)
    except Exception as e:  # noqa: BLE001
        logger.warning("ga_structured_failed", error=str(e))
        return []

    return [
        {
            "path": row.dimension_values[0].value,
            "sessions": int(row.metric_values[0].value or 0),
            "views": int(row.metric_values[1].value or 0),
        }
        for row in response.rows
    ]


def fetch_summary(*, org_id: str, days: int = 7) -> str:
    """Return a short human-readable GA4 summary for the Analyst agent."""
    tokens = _load_tokens(org_id)
    if tokens is None:
        return (
            "Google Analytics is not connected for this org. "
            "Connect it from the Integrations page to unlock real traffic data."
        )

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        from google.oauth2.credentials import Credentials
    except Exception as e:
        return f"google-analytics-data not available: {e}"

    creds = Credentials(
        token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token") or None,
    )

    try:
        client = BetaAnalyticsDataClient(credentials=creds)
        end = datetime.utcnow().date()
        start = end - timedelta(days=days)
        request = RunReportRequest(
            property=f"properties/{tokens['property_id']}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="totalUsers"),
            ],
            date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
            limit=5,
        )
        response = client.run_report(request)
    except Exception as e:
        logger.warning("ga_report_failed", error=str(e))
        return f"GA report failed: {e}"

    lines: list[str] = [
        f"Google Analytics — last {days} days (top pages):",
    ]
    for row in response.rows:
        page = row.dimension_values[0].value
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        lines.append(f"- {page}: {views} views, {users} users")
    if len(lines) == 1:
        lines.append("- no traffic recorded in the window")
    return "\n".join(lines)
