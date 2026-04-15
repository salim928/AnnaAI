"""External webhook handlers — primarily Paystack billing events."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from db.client import get_supabase_admin_client
from integrations.paystack import verify_webhook
from utils.logger import get_logger

logger = get_logger("webhooks")
router = APIRouter()


def _plan_from_event(data: dict[str, Any]) -> str | None:
    metadata = data.get("metadata") or {}
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            metadata = {}
    return metadata.get("plan") if isinstance(metadata, dict) else None


def _org_from_event(data: dict[str, Any]) -> str | None:
    metadata = data.get("metadata") or {}
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            metadata = {}
    return metadata.get("org_id") if isinstance(metadata, dict) else None


@router.post("/paystack")
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str = Header(default=""),
) -> dict[str, str]:
    body = await request.body()
    if not verify_webhook(body, x_paystack_signature):
        raise HTTPException(401, "invalid signature")

    try:
        payload = json.loads(body.decode())
    except json.JSONDecodeError:
        raise HTTPException(400, "invalid payload")

    event = payload.get("event", "")
    data = payload.get("data", {}) or {}
    logger.info("paystack.webhook", event=event)

    sb = get_supabase_admin_client()

    if event == "charge.success":
        org_id = _org_from_event(data)
        plan = _plan_from_event(data) or "pro"
        if org_id:
            sb.table("organizations").update({"plan": plan}).eq("id", org_id).execute()
            logger.info("paystack.plan.upgraded", org_id=org_id, plan=plan)

    elif event in ("subscription.disable", "subscription.not_renew"):
        org_id = _org_from_event(data)
        if org_id:
            sb.table("organizations").update({"plan": "free"}).eq("id", org_id).execute()
            logger.info("paystack.plan.downgraded", org_id=org_id)

    return {"status": "ok"}
