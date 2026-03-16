from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


RunStatus = Literal["queued", "running", "completed", "failed"]
StageStatus = Literal["pending", "running", "completed", "failed"]


class Citation(BaseModel):
    title: str
    url: str
    snippet: str | None = None
    source: str = "web"


class StageOutput(BaseModel):
    stage_name: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    handoff: dict[str, Any] = Field(default_factory=dict)
    citations: list[Citation] = Field(default_factory=list)
    markdown: str
    raw_text: str | None = None


class RunEvent(BaseModel):
    event_type: str
    payload: dict[str, Any]
    created_at: datetime


class StageRunRecord(BaseModel):
    stage_index: int
    stage_name: str
    status: StageStatus
    provider_name: str | None = None
    model_name: str | None = None
    summary: str | None = None
    markdown: str | None = None
    handoff: dict[str, Any] = Field(default_factory=dict)
    citations: list[Citation] = Field(default_factory=list)
    raw_text: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class AnalysisRunRecord(BaseModel):
    owner_email: str | None = None
    project_public_id: str | None = None
    public_id: str
    idea_text: str
    status: RunStatus
    current_stage: int | None = None
    current_stage_name: str | None = None
    final_markdown: str | None = None
    failure_message: str | None = None
    created_at: datetime
    updated_at: datetime
    stages: list[StageRunRecord] = Field(default_factory=list)
    events: list[RunEvent] = Field(default_factory=list)


class AnalysisRunSummary(BaseModel):
    owner_email: str | None = None
    project_public_id: str | None = None
    public_id: str
    idea_text: str
    status: RunStatus
    current_stage_name: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectSummary(BaseModel):
    owner_email: str | None = None
    public_id: str
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    run_count: int = 0


class UserSummary(BaseModel):
    email: str
    role: Literal["user", "admin"]
    created_at: datetime
    updated_at: datetime


class SubscriptionRecord(BaseModel):
    email: str
    plan_name: str
    status: str
    created_at: datetime
    updated_at: datetime


class CreateRunRequest(BaseModel):
    idea_text: str = Field(min_length=20, max_length=4000)
    project_public_id: str | None = None


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=400)


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class ProviderResponse(BaseModel):
    provider_name: str
    model_name: str
    text: str


class SearchResultBundle(BaseModel):
    query: str
    results: list[Citation] = Field(default_factory=list)


class PageMeta(BaseModel):
    title: str
    description: str
    canonical_url: str
    robots: str = "index,follow"
    og_type: str = "website"
    structured_data: list[dict[str, Any]] = Field(default_factory=list)
