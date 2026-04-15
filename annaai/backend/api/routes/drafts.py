"""Content drafts — list, get, update, approve, reject, publish."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from db.client import get_supabase_admin_client
from db.models import (
    ContentDraftResponse,
    ContentDraftUpdate,
    PaginatedResponse,
)
from dependencies import CurrentOrgUser
from memory.vector_store import store_feedback_chunk
from utils.logger import get_logger

logger = get_logger("drafts")
router = APIRouter()


def _sb():
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    return sb


@router.get("", response_model=PaginatedResponse[ContentDraftResponse])
async def list_drafts(
    user: CurrentOrgUser,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ContentDraftResponse]:
    sb = _sb()
    start = (page - 1) * page_size
    end = start + page_size - 1
    query = (
        sb.table("content_drafts")
        .select("*", count="exact")
        .eq("org_id", user.org_id)
        .order("created_at", desc=True)
        .range(start, end)
    )
    if status_filter:
        query = query.eq("status", status_filter)
    try:
        res = query.execute()
    except Exception as e:
        raise HTTPException(500, f"drafts query failed: {e}") from e

    items = [ContentDraftResponse.model_validate(row) for row in (res.data or [])]
    total = int(res.count or 0)
    return PaginatedResponse[ContentDraftResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(start + len(items)) < total,
    )


@router.get("/{draft_id}", response_model=ContentDraftResponse)
async def get_draft(draft_id: str, user: CurrentOrgUser) -> ContentDraftResponse:
    sb = _sb()
    try:
        res = (
            sb.table("content_drafts")
            .select("*")
            .eq("id", draft_id)
            .eq("org_id", user.org_id)
            .single()
            .execute()
        )
    except Exception as e:
        raise HTTPException(404, f"draft not found: {e}") from e
    return ContentDraftResponse.model_validate(res.data)


@router.patch("/{draft_id}", response_model=ContentDraftResponse)
async def update_draft(
    draft_id: str,
    payload: ContentDraftUpdate,
    user: CurrentOrgUser,
) -> ContentDraftResponse:
    sb = _sb()
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(400, "no fields to update")
    try:
        res = (
            sb.table("content_drafts")
            .update(updates)
            .eq("id", draft_id)
            .eq("org_id", user.org_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"update failed: {e}") from e
    if not res.data:
        raise HTTPException(404, "draft not found")
    return ContentDraftResponse.model_validate(res.data[0])


@router.post("/{draft_id}/approve", response_model=ContentDraftResponse)
async def approve_draft(draft_id: str, user: CurrentOrgUser) -> ContentDraftResponse:
    sb = _sb()
    try:
        res = (
            sb.table("content_drafts")
            .update({"status": "approved"})
            .eq("id", draft_id)
            .eq("org_id", user.org_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"approve failed: {e}") from e
    if not res.data:
        raise HTTPException(404, "draft not found")
    draft = res.data[0]

    # Positive feedback for the learning loop
    try:
        store_feedback_chunk(
            user.org_id or "",
            f"Content that worked well: {draft.get('title','')}. Topic: {draft.get('topic','')}.",
            chunk_type="positive_feedback",
        )
    except Exception as e:
        logger.warning("positive_feedback_store_failed", error=str(e))

    return ContentDraftResponse.model_validate(draft)


@router.post("/{draft_id}/reject", response_model=ContentDraftResponse)
async def reject_draft(
    draft_id: str,
    user: CurrentOrgUser,
    reason: str = Query(..., min_length=1, max_length=500),
) -> ContentDraftResponse:
    sb = _sb()
    try:
        res = (
            sb.table("content_drafts")
            .update({"status": "rejected", "rejection_reason": reason})
            .eq("id", draft_id)
            .eq("org_id", user.org_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"reject failed: {e}") from e
    if not res.data:
        raise HTTPException(404, "draft not found")
    draft = res.data[0]

    try:
        store_feedback_chunk(
            user.org_id or "",
            f"Do NOT write content like this: {draft.get('title','')}. Reason: {reason}",
            chunk_type="negative_feedback",
        )
    except Exception as e:
        logger.warning("negative_feedback_store_failed", error=str(e))

    return ContentDraftResponse.model_validate(draft)
