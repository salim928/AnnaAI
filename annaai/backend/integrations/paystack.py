"""Paystack integration — GHS subscription billing."""
from __future__ import annotations

import hashlib
import hmac
from typing import Any

import httpx

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

PAYSTACK_API = "https://api.paystack.co"

PLANS: dict[str, dict[str, Any]] = {
    "pro": {
        "code": "PLN_annaai_pro",
        "name": "AnnaAi Pro",
        "amount_kobo": 12_000_00,  # GHS 120.00 in minor units
        "currency": "GHS",
        "interval": "monthly",
    },
    "business": {
        "code": "PLN_annaai_business",
        "name": "AnnaAi Business",
        "amount_kobo": 48_000_00,  # GHS 480.00
        "currency": "GHS",
        "interval": "monthly",
    },
}


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


async def initialize_transaction(
    email: str,
    plan: str,
    org_id: str,
    callback_url: str | None = None,
) -> dict[str, Any]:
    """Start a checkout session for the given plan. Returns authorization URL."""
    if not settings.PAYSTACK_SECRET_KEY:
        raise RuntimeError("Paystack not configured")
    if plan not in PLANS:
        raise ValueError(f"Unknown plan: {plan}")

    payload = {
        "email": email,
        "amount": PLANS[plan]["amount_kobo"],
        "currency": PLANS[plan]["currency"],
        "plan": PLANS[plan]["code"],
        "callback_url": callback_url or f"{settings.FRONTEND_URL}/settings?tab=billing",
        "metadata": {
            "org_id": org_id,
            "plan": plan,
        },
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(
            f"{PAYSTACK_API}/transaction/initialize",
            json=payload,
            headers=_headers(),
        )
        res.raise_for_status()
        data = res.json()

    logger.info("paystack.init.ok", org_id=org_id, plan=plan)
    return data.get("data", {})


async def verify_transaction(reference: str) -> dict[str, Any]:
    if not settings.PAYSTACK_SECRET_KEY:
        raise RuntimeError("Paystack not configured")
    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.get(
            f"{PAYSTACK_API}/transaction/verify/{reference}",
            headers=_headers(),
        )
        res.raise_for_status()
        return res.json().get("data", {})


def verify_webhook(body: bytes, signature: str | None) -> bool:
    if not signature or not settings.PAYSTACK_SECRET_KEY:
        return False
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
