"""CrewAI 1.9 agent tools — zero langchain imports.

Every tool uses `@tool` from `crewai.tools`. Tools read the active org
from a contextvar, which the pipeline sets before `crew.kickoff()`.
"""
from __future__ import annotations

import contextvars
from typing import Any
from urllib.parse import quote

from crewai.tools import tool
from duckduckgo_search import DDGS

from config import settings
from db.client import get_supabase_admin_client
from memory.vector_store import recall_brand_memory as _recall
from utils.helpers import generate_slug, truncate_text
from utils.logger import get_logger

logger = get_logger("tools")

# The pipeline sets this for the duration of a single kickoff() so tools
# know which tenant they are acting on without every call passing org_id.
_current_org_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "anna_current_org_id", default=None
)
_current_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "anna_current_run_id", default=None
)


def set_agent_context(*, org_id: str, run_id: str | None = None) -> None:
    _current_org_id.set(org_id)
    _current_run_id.set(run_id)


def _org_id() -> str:
    org = _current_org_id.get()
    if not org:
        raise RuntimeError(
            "No active org_id — call set_agent_context(org_id=...) before crew.kickoff()"
        )
    return org


# ---------------------------------------------------------------------------
# Brand memory
# ---------------------------------------------------------------------------
@tool("recall_brand_memory")
def recall_brand_memory(query: str) -> str:
    """Retrieve brand voice, positioning, and product snippets from memory.

    Call this before writing anything so the output matches the business's
    actual voice. Also retrieves positive/negative feedback chunks saved
    from approved and rejected drafts.
    """
    chunks = _recall(_org_id(), query, top_k=5)
    if not chunks:
        return "No brand memory available for that query."
    return "\n---\n".join(chunks)


# ---------------------------------------------------------------------------
# Web search
# ---------------------------------------------------------------------------
@tool("search_web")
def search_web(query: str) -> str:
    """Free DuckDuckGo web search. Returns title, snippet, and URL for the top results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))
    except Exception as e:
        logger.warning("search_web_failed", error=str(e))
        return f"search failed: {e}"
    if not results:
        return "No results found."
    lines: list[str] = []
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href") or r.get("url", "")
        lines.append(f"- {title} ({href})\n  {body}")
    return "\n".join(lines)


@tool("search_competitor_content")
def search_competitor_content(domain: str) -> str:
    """Find recent headlines from a specific competitor domain. Input: a domain like 'techcabal.com'."""
    query = f"site:{domain}"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))
    except Exception as e:
        return f"competitor search failed: {e}"
    if not results:
        return f"No recent content found for {domain}."
    return "\n".join(f"- {r.get('title','')} ({r.get('href','')})" for r in results)


@tool("get_trending_topics")
def get_trending_topics(industry: str) -> str:
    """Surface this week's trending topics in an industry via DuckDuckGo."""
    query = f"{industry} trends this week 2026"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10))
    except Exception as e:
        return f"trending search failed: {e}"
    if not results:
        return "No trending topics found."
    return "\n".join(f"- {r.get('title','')}\n  {r.get('body','')}" for r in results[:8])


# ---------------------------------------------------------------------------
# Analytics (real integration module lives in integrations/google_analytics.py)
# ---------------------------------------------------------------------------
@tool("get_analytics_summary")
def get_analytics_summary(days: int = 7) -> str:
    """Return a short Google Analytics summary for the active org.

    Falls back to a neutral placeholder when GA is not connected so the
    Analyst agent can still proceed on first runs.
    """
    try:
        from integrations.google_analytics import fetch_summary

        return fetch_summary(org_id=_org_id(), days=days)
    except Exception as e:
        logger.warning("ga_summary_failed", error=str(e))
        return (
            "No Google Analytics data available yet. "
            "Connect Google in Integrations to unlock real traffic insights."
        )


@tool("get_search_console_data")
def get_search_console_data(days: int = 30) -> str:
    """Return top keywords from Google Search Console for the active org."""
    try:
        from integrations.google_search_console import fetch_top_keywords

        return fetch_top_keywords(org_id=_org_id(), days=days)
    except Exception as e:
        logger.warning("gsc_fetch_failed", error=str(e))
        return "Google Search Console not connected."


# ---------------------------------------------------------------------------
# Image generation — Pollinations.ai is free and keyless
# ---------------------------------------------------------------------------
@tool("generate_image")
def generate_image(prompt: str) -> str:
    """Generate a hero image via Pollinations.ai. Returns the image URL (PNG)."""
    safe = quote(prompt)[:500]
    url = (
        f"{settings.POLLINATIONS_BASE_URL}/{safe}"
        f"?width={settings.POLLINATIONS_WIDTH}"
        f"&height={settings.POLLINATIONS_HEIGHT}"
        f"&nologo=true&enhance=true"
    )
    return url


# ---------------------------------------------------------------------------
# WordPress (lazy import so Batch 2 compiles without Batch 3 integrations)
# ---------------------------------------------------------------------------
@tool("get_wordpress_recent_posts")
def get_wordpress_recent_posts(limit: int = 5) -> str:
    """List the 5 most recent WordPress posts for the active org."""
    try:
        from integrations.wordpress import list_recent_posts

        return list_recent_posts(org_id=_org_id(), limit=limit)
    except Exception as e:
        return f"WordPress not connected: {e}"


@tool("publish_to_wordpress")
def publish_to_wordpress(title: str, content: str, status: str = "draft") -> str:
    """Create a WordPress post. status should be 'draft' unless explicitly approved."""
    try:
        from integrations.wordpress import create_post

        return create_post(org_id=_org_id(), title=title, content=content, status=status)
    except Exception as e:
        return f"WordPress publish failed: {e}"


# ---------------------------------------------------------------------------
# Email brief
# ---------------------------------------------------------------------------
@tool("send_daily_brief")
def send_daily_brief(subject: str, html_body: str) -> str:
    """Send the daily brief email to the org's notification_email."""
    try:
        from integrations.email_sender import send_daily_brief as _send

        return _send(org_id=_org_id(), subject=subject, html_body=html_body)
    except Exception as e:
        logger.warning("send_daily_brief_failed", error=str(e))
        return f"email send failed: {e}"


# ---------------------------------------------------------------------------
# Drafts
# ---------------------------------------------------------------------------
@tool("save_content_draft")
def save_content_draft(
    type: str,
    title: str,
    body: str,
    meta_description: str = "",
    image_url: str = "",
    topic: str = "",
) -> str:
    """Persist a content draft to Supabase. Returns the new draft id (or 'local' fallback)."""
    sb = get_supabase_admin_client()
    row: dict[str, Any] = {
        "org_id": _org_id(),
        "run_id": _current_run_id.get(),
        "type": type,
        "title": truncate_text(title, 200),
        "body": body,
        "meta_description": truncate_text(meta_description, 180) if meta_description else None,
        "image_url": image_url or None,
        "topic": topic or None,
        "status": "draft",
    }
    if sb is None:
        logger.warning("save_draft_no_supabase", title=row["title"])
        return f"local:{generate_slug(title)}"
    try:
        res = sb.table("content_drafts").insert(row).execute()
        draft_id = (res.data or [{}])[0].get("id", "unknown")
        logger.info("draft_saved", draft_id=draft_id, type=type)
        return str(draft_id)
    except Exception as e:
        logger.error("save_draft_failed", error=str(e))
        return f"save failed: {e}"


# ---------------------------------------------------------------------------
# SEO helper
# ---------------------------------------------------------------------------
@tool("calculate_seo_score")
def calculate_seo_score(title: str, body: str, target_keyword: str) -> str:
    """Rough SEO score 0-100 plus actionable notes. Heuristic — no external API."""
    notes: list[str] = []
    score = 100

    words = body.split()
    word_count = len(words)
    if word_count < 300:
        score -= 20
        notes.append(f"body is only {word_count} words; aim for 400-800")
    elif word_count > 1500:
        score -= 5
        notes.append("body is quite long; consider tightening")

    kw = target_keyword.lower().strip()
    if kw:
        title_hit = kw in title.lower()
        body_hits = body.lower().count(kw)
        if not title_hit:
            score -= 15
            notes.append("target keyword missing from title")
        if body_hits == 0:
            score -= 20
            notes.append("target keyword missing from body")
        elif body_hits > word_count / 40:
            score -= 10
            notes.append("keyword density too high — reads as spam")

    if body.count("##") < 2:
        score -= 10
        notes.append("use at least 2 H2 subheadings for scannability")

    score = max(0, min(100, score))
    return f"SEO score: {score}/100\n" + ("\n".join(f"- {n}" for n in notes) if notes else "- looks good")


# ---------------------------------------------------------------------------
# Convenience bundles
# ---------------------------------------------------------------------------
RESEARCHER_TOOLS = [search_web, search_competitor_content, get_trending_topics]
ANALYST_TOOLS = [get_analytics_summary, get_search_console_data]
STRATEGIST_TOOLS = [recall_brand_memory, calculate_seo_score]
CREATOR_TOOLS = [recall_brand_memory, generate_image, calculate_seo_score]
PUBLISHER_TOOLS = [
    save_content_draft,
    publish_to_wordpress,
    get_wordpress_recent_posts,
    send_daily_brief,
]
