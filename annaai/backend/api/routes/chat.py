"""Chat with Anna — Anthropic streaming over SSE."""
from __future__ import annotations

import json
from collections.abc import AsyncIterator

from anthropic import Anthropic
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from db.client import get_supabase_admin_client
from dependencies import CurrentOrgUser
from memory.vector_store import get_brand_memory_summary
from utils.logger import get_logger

logger = get_logger("chat")
router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: list[dict[str, str]] = Field(default_factory=list)


def _system_prompt(org_id: str) -> str:
    brand_context = get_brand_memory_summary(org_id)
    return (
        "You are Anna, an autonomous AI marketing agent talking to the founder.\n"
        "You are warm, proactive, and concise. You suggest next steps without "
        "being pushy. Use the brand memory below to stay on-voice.\n\n"
        f"BRAND MEMORY:\n{brand_context}"
    )


async def _stream(org_id: str, message: str, history: list[dict[str, str]]) -> AsyncIterator[bytes]:
    if not settings.ANTHROPIC_API_KEY:
        yield b'data: {"error": "ANTHROPIC_API_KEY not set"}\n\n'
        yield b"data: [DONE]\n\n"
        return

    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    messages: list[dict[str, str]] = []
    for msg in history[-10:]:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    try:
        with client.messages.stream(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            system=_system_prompt(org_id),
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                if text:
                    payload = json.dumps({"delta": text})
                    yield f"data: {payload}\n\n".encode()
    except Exception as e:
        logger.error("chat_stream_failed", error=str(e))
        err = json.dumps({"error": str(e)})
        yield f"data: {err}\n\n".encode()

    yield b"data: [DONE]\n\n"


@router.post("/message")
async def chat_message(payload: ChatRequest, user: CurrentOrgUser) -> StreamingResponse:
    sb = get_supabase_admin_client()
    if sb is not None:
        try:
            sb.table("chat_messages").insert(
                {
                    "org_id": user.org_id,
                    "user_id": user.user_id,
                    "role": "user",
                    "content": payload.message,
                }
            ).execute()
        except Exception as e:
            logger.warning("chat_log_failed", error=str(e))

    return StreamingResponse(
        _stream(user.org_id or "", payload.message, payload.history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history")
async def chat_history(user: CurrentOrgUser, limit: int = 50) -> dict[str, list[dict]]:
    sb = get_supabase_admin_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    try:
        res = (
            sb.table("chat_messages")
            .select("id,role,content,created_at")
            .eq("org_id", user.org_id)
            .order("created_at", desc=True)
            .limit(max(1, min(200, limit)))
            .execute()
        )
    except Exception as e:
        raise HTTPException(500, f"history query failed: {e}") from e
    return {"messages": list(reversed(res.data or []))}
