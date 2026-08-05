"""Stable browser contracts for the run-scoped Agent API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class RunSummary(BaseModel):
    id: str
    state: str
    revision: int
    provider: str
    model: str
    current_version_id: str | None
    created_at: datetime


class RunListResponse(BaseModel):
    items: list[RunSummary]
    next_cursor: str | None = None


class ResourceRecord(BaseModel):
    id: str
    created_at: datetime


class MessageRecord(ResourceRecord):
    sequence: int
    role: str
    content: str


class ProposalRecord(ResourceRecord):
    revision: int
    status: str
    affected_content: str
    suggested_replacement: str
    jd_reason: str
    source_evidence: dict[str, Any]
    evidence_request: str | None = None


class DecisionRecord(ResourceRecord):
    proposal_id: str
    proposal_revision: int
    decision: str
    version_id: str | None


class VersionRecord(ResourceRecord):
    version_number: int
    version_name: str
    parent_version_id: str | None
    content: dict[str, Any]


class ExportRecord(ResourceRecord):
    version_id: str
    content_type: str
    size_bytes: int


class ResumeSource(BaseModel):
    id: str
    filename: str
    parsed_data: dict[str, Any]


class JobDescriptionSource(BaseModel):
    id: str
    raw_text: str
    analysis: dict[str, Any]


class RunSnapshotResponse(BaseModel):
    run: RunSummary
    resume: ResumeSource | None
    job_description: JobDescriptionSource | None
    messages: list[MessageRecord]
    proposals: list[ProposalRecord]
    decisions: list[DecisionRecord]
    versions: list[VersionRecord]
    exports: list[ExportRecord]
    latest_event_sequence: int


class JobDescriptionRequest(BaseModel):
    content: str = Field(min_length=50, max_length=100_000)


class MessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)


class EvidenceRequest(BaseModel):
    content: str = Field(min_length=2, max_length=20_000)


class ProposalDecisionRequest(BaseModel):
    decision: Literal["accepted", "rejected", "revision_requested"]
    expected_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=8, max_length=255)
    version_name: str | None = Field(default=None, max_length=255)


class RestoreVersionRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=255)


class CreateExportRequest(BaseModel):
    format: Literal["pdf", "docx"]
    idempotency_key: str = Field(min_length=8, max_length=255)
