"""Auth routes — thin wrapper over Supabase Python v2 auth."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from db.client import get_supabase_client
from utils.logger import get_logger

logger = get_logger("auth")
router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = None
    org_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    user_id: str
    email: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> Any:
    sb = get_supabase_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    try:
        result = sb.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {
                    "data": {
                        "full_name": payload.full_name or "",
                        "org_name": payload.org_name or "",
                    }
                },
            }
        )
    except Exception as e:
        logger.warning("register_failed", email=payload.email, error=str(e))
        raise HTTPException(400, f"register failed: {e}") from e

    if not result.user or not result.session:
        raise HTTPException(400, "registration incomplete — confirm email")

    return TokenResponse(
        access_token=result.session.access_token,
        refresh_token=result.session.refresh_token,
        user_id=result.user.id,
        email=result.user.email or payload.email,
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> Any:
    sb = get_supabase_client()
    if sb is None:
        raise HTTPException(503, "Supabase not configured")
    try:
        result = sb.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception as e:
        logger.warning("login_failed", email=payload.email, error=str(e))
        raise HTTPException(401, "invalid credentials") from e

    if not result.user or not result.session:
        raise HTTPException(401, "invalid credentials")

    return TokenResponse(
        access_token=result.session.access_token,
        refresh_token=result.session.refresh_token,
        user_id=result.user.id,
        email=result.user.email or payload.email,
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    sb = get_supabase_client()
    if sb is None:
        return {"status": "ok"}
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    return {"status": "ok"}
