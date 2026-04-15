"""Pydantic v2 API models."""
from __future__ import annotations

from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

ORM = ConfigDict(from_attributes=True, populate_by_name=True)

T = TypeVar("T")


# --- Organizations ----------------------------------------------------------
class OrgCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    website_url: HttpUrl | None = None
    industry: str | None = None


class OrgResponse(BaseModel):
    model_config = ORM

    id: str
    name: str
    website_url: str | None = None
    industry: str | None = None
    brand_voice: str | None = None
    plan: str = "free"
    onboarding_complete: bool = False
    onboarding_step: int = 0
    created_at: datetime


class OrgUpdate(BaseModel):
    name: str | None = None
    website_url: HttpUrl | None = None
    industry: str | None = None
    brand_voice: str | None = None
    brand_tone: str | None = None
    target_audience: str | None = None
    goals: str | None = None
    notification_email: EmailStr | None = None


# --- Users ------------------------------------------------------------------
class UserResponse(BaseModel):
    model_config = ORM

    id: str
    email: EmailStr
    full_name: str | None = None
    org_id: str | None = None
    role: str = "owner"


# --- Agent runs -------------------------------------------------------------
class AgentRunResponse(BaseModel):
    model_config = ORM

    id: str
    org_id: str
    status: Literal["running", "completed", "failed"]
    run_type: str
    summary: str | None = None
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


# --- Content drafts ---------------------------------------------------------
class ContentDraftResponse(BaseModel):
    model_config = ORM

    id: str
    org_id: str
    run_id: str | None = None
    type: str
    title: str | None = None
    body: str | None = None
    meta_description: str | None = None
    image_url: str | None = None
    topic: str | None = None
    keywords: list[str] = Field(default_factory=list)
    status: Literal["draft", "approved", "published", "rejected"]
    rejection_reason: str | None = None
    platform_url: str | None = None
    performance_label: str | None = None
    created_at: datetime
    updated_at: datetime


class ContentDraftUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    meta_description: str | None = None
    status: Literal["draft", "approved", "published", "rejected"] | None = None
    rejection_reason: str | None = None


# --- Chat -------------------------------------------------------------------
class ChatMessageResponse(BaseModel):
    model_config = ORM

    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)


# --- Onboarding -------------------------------------------------------------
class OnboardingStatusResponse(BaseModel):
    onboarding_complete: bool
    onboarding_step: int
    total_steps: int = 4
    current_step_name: str | None = None


# --- Run stats --------------------------------------------------------------
class RunStatsResponse(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    total_drafts: int
    published_drafts: int
    avg_duration_seconds: float


# --- Pagination -------------------------------------------------------------
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_more: bool
