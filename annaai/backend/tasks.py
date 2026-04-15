"""Celery app, beat schedule, and asynchronous task definitions."""
from __future__ import annotations

import asyncio

from celery import Celery
from celery.schedules import crontab

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

celery_app = Celery(
    "annaai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=60 * 30,
    task_soft_time_limit=60 * 25,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

celery_app.conf.beat_schedule = {
    "daily-anna-run": {
        "task": "tasks.run_daily_for_all_orgs",
        "schedule": crontab(hour=6, minute=0),
    },
    "collect-published-metrics": {
        "task": "tasks.collect_published_metrics",
        "schedule": crontab(hour=3, minute=0),
    },
}


def _run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
    except RuntimeError:
        pass
    return asyncio.run(coro)


@celery_app.task(name="tasks.run_daily_for_all_orgs", bind=True, max_retries=2)
def run_daily_for_all_orgs(self) -> dict:
    from agents.pipeline import run_daily_pipeline_for_all_orgs

    logger.info("celery.daily_run.start")
    try:
        result = _run_async(run_daily_pipeline_for_all_orgs())
    except Exception as exc:  # noqa: BLE001
        logger.exception("celery.daily_run.failed")
        raise self.retry(exc=exc, countdown=300)
    logger.info("celery.daily_run.done", result=result)
    return result


@celery_app.task(name="tasks.run_daily_for_org", bind=True, max_retries=2)
def run_daily_for_org(self, org_id: str) -> dict:
    from agents.pipeline import run_daily_pipeline_for_org

    logger.info("celery.org_run.start", org_id=org_id)
    try:
        result = _run_async(run_daily_pipeline_for_org(org_id))
    except Exception as exc:  # noqa: BLE001
        logger.exception("celery.org_run.failed", org_id=org_id)
        raise self.retry(exc=exc, countdown=180)
    return result


@celery_app.task(name="tasks.run_onboarding", bind=True, max_retries=1)
def run_onboarding(self, org_id: str, website_url: str) -> dict:
    from agents.pipeline import run_onboarding_pipeline

    logger.info("celery.onboarding.start", org_id=org_id, url=website_url)
    try:
        result = _run_async(run_onboarding_pipeline(org_id, website_url))
    except Exception as exc:  # noqa: BLE001
        logger.exception("celery.onboarding.failed", org_id=org_id)
        raise self.retry(exc=exc, countdown=120)
    return result


@celery_app.task(name="tasks.collect_published_metrics")
def collect_published_metrics() -> dict:
    """Pull GA4 metrics for published drafts, label performance, learn from winners."""
    from db.client import get_supabase_admin_client
    from integrations.google_analytics import fetch_top_pages
    from memory.vector_store import store_feedback_chunk

    logger.info("metrics.collect.start")
    sb = get_supabase_admin_client()
    if sb is None:
        return {"updated": 0, "skipped": "supabase unavailable"}

    try:
        published = (
            sb.table("content_drafts")
            .select("id, org_id, title, body, platform_url")
            .eq("status", "published")
            .not_.is_("platform_url", "null")
            .limit(200)
            .execute()
        )
    except Exception:  # noqa: BLE001
        logger.exception("metrics.collect.fetch_failed")
        return {"updated": 0}

    by_org: dict[str, list[dict]] = {}
    for row in published.data or []:
        by_org.setdefault(row["org_id"], []).append(row)

    updated = 0
    winners = 0

    for org_id, drafts in by_org.items():
        top_pages = fetch_top_pages(org_id=org_id, days=30, limit=100)
        if not top_pages:
            continue

        page_lookup = {p["path"]: p["sessions"] for p in top_pages}
        sessions_sorted = sorted(page_lookup.values())
        if len(sessions_sorted) >= 4:
            p75 = sessions_sorted[int(len(sessions_sorted) * 0.75)]
            p25 = sessions_sorted[int(len(sessions_sorted) * 0.25)]
        else:
            p75 = max(sessions_sorted) if sessions_sorted else 0
            p25 = 0

        for draft in drafts:
            url = draft.get("platform_url") or ""
            matched = next(
                (v for k, v in page_lookup.items() if k and k in url),
                None,
            )
            if matched is None:
                continue

            label = (
                "high_performer"
                if matched >= p75 and matched > 0
                else "low_performer"
                if matched <= p25
                else "average"
            )

            try:
                sb.table("content_metrics").insert(
                    {
                        "draft_id": draft["id"],
                        "page_views": matched,
                    }
                ).execute()
                sb.table("content_drafts").update(
                    {"performance_label": label}
                ).eq("id", draft["id"]).execute()
                updated += 1

                if label == "high_performer" and draft.get("body"):
                    try:
                        store_feedback_chunk(
                            org_id=org_id,
                            text=f"High-performing post: {draft.get('title', '')}\n\n{draft['body'][:1500]}",
                            chunk_type="positive_feedback",
                        )
                        winners += 1
                    except Exception:  # noqa: BLE001
                        logger.warning("metrics.collect.memory_failed", draft_id=draft["id"])
            except Exception:  # noqa: BLE001
                logger.warning("metrics.collect.upsert_failed", draft_id=draft["id"])

    logger.info("metrics.collect.done", updated=updated, winners_learned=winners)
    return {"updated": updated, "winners_learned": winners}
