"""Billing routes — plan info + Paystack checkout initialization."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db.client import get_supabase_admin_client
from dependencies import CurrentOrgUser
from integrations.paystack import PLANS, initialize_transaction
from utils.logger import get_logger

logger = get_logger("billing")
router = APIRouter()


class PlanInfo(BaseModel):
    key: str
    name: str
    price_ghs: float
    interval: str


class CheckoutRequest(BaseModel):
    plan: str = Field(..., pattern="^(pro|business)$")


class CheckoutResponse(BaseModel):
    authorization_url: str
    reference: str


@router.get("/plans", response_model=list[PlanInfo])
async def list_plans() -> list[PlanInfo]:
    return [
        PlanInfo(
            key=key,
            name=p["name"],
            price_ghs=p["amount_kobo"] / 100,
            interval=p["interval"],
        )
        for key, p in PLANS.items()
    ]


@router.get("/current")
async def current_plan(user: CurrentOrgUser) -> dict[str, str]:
    sb = get_supabase_admin_client()
    res = (
        sb.table("organizations")
        .select("plan")
        .eq("id", user["org_id"])
        .single()
        .execute()
    )
    return {"plan": res.data.get("plan", "free") if res.data else "free"}


@router.post("/checkout", response_model=CheckoutResponse)
async def start_checkout(
    body: CheckoutRequest,
    user: CurrentOrgUser,
) -> CheckoutResponse:
    try:
        data = await initialize_transaction(
            email=user["email"],
            plan=body.plan,
            org_id=user["org_id"],
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:  # noqa: BLE001
        logger.exception("billing.checkout.failed")
        raise HTTPException(500, f"checkout failed: {e}")

    return CheckoutResponse(
        authorization_url=data["authorization_url"],
        reference=data["reference"],
    )
