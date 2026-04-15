"""FastAPI dependency aliases — JWT auth + org scoping.

Full JWT validation and Supabase user lookup land in Batch 3.
This module exposes the typed Annotated aliases routes should import.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status

from config import settings
from db.client import get_supabase_admin_client


@dataclass(slots=True, frozen=True)
class AuthenticatedUser:
    user_id: str
    email: str
    org_id: str | None


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY or "",
            algorithms=["HS256", "ES256", "RS256"],
            options={"verify_signature": False, "verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        ) from exc

    user_id = payload.get("sub") or payload.get("user_id")
    email = payload.get("email", "")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject"
        )

    org_id: str | None = payload.get("org_id")
    if not org_id:
        client = get_supabase_admin_client()
        if client is not None:
            try:
                res = client.table("users").select("org_id").eq("id", user_id).single().execute()
                org_id = (res.data or {}).get("org_id")
            except Exception:
                org_id = None

    return AuthenticatedUser(user_id=user_id, email=email, org_id=org_id)


async def require_org(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> AuthenticatedUser:
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not attached to an organisation",
        )
    return user


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
CurrentOrgUser = Annotated[AuthenticatedUser, Depends(require_org)]
