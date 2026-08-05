"""Authenticated, run-scoped browser API for the resume tailoring Agent."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response, StreamingResponse

from ...api.auth import UserContext, get_current_user
from ...infra.storage.workflow_repository import ResourceNotFoundError, StaleRevisionError
from ...wiring import (
    get_export_storage_service,
    get_object_storage,
    get_tailoring_orchestrator,
    get_workflow_repository,
)
from ..schemas.agent import (
    CreateExportRequest,
    DecisionRecord,
    ExportRecord,
    EvidenceRequest,
    JobDescriptionRequest,
    JobDescriptionSource,
    MessageRecord,
    MessageRequest,
    ProposalDecisionRequest,
    ProposalRecord,
    RestoreVersionRequest,
    ResumeSource,
    RunListResponse,
    RunSnapshotResponse,
    RunSummary,
    VersionRecord,
)


router = APIRouter(prefix="/agent", tags=["Resume Agent"])


def _not_found(exc: Exception):
    raise HTTPException(status_code=404, detail="Resource not found") from exc


def _conflict(exc: Exception):
    raise HTTPException(status_code=409, detail=str(exc)) from exc


def _run(item) -> RunSummary:
    return RunSummary(
        id=item.id, state=item.state, revision=item.revision,
        provider=item.provider, model=item.model,
        current_version_id=item.current_version_id, created_at=item.created_at,
    )


def _snapshot(value) -> RunSnapshotResponse:
    return RunSnapshotResponse(
        run=_run(value.run),
        resume=(ResumeSource(id=value.master_resume.id, filename=value.master_resume.filename,
                             parsed_data=value.master_resume.parsed_data)
                if value.master_resume else None),
        job_description=(JobDescriptionSource(
            id=value.job_description.id, raw_text=value.job_description.raw_text,
            analysis=value.job_description.analysis_result,
        ) if value.job_description else None),
        messages=[MessageRecord(id=x.id, sequence=x.sequence, role=x.role,
                                content=x.content, created_at=x.created_at)
                  for x in value.messages],
        proposals=[ProposalRecord(
            id=x.id, revision=x.revision, status=x.status,
            affected_content=x.original_text, suggested_replacement=x.suggested_text,
            jd_reason=x.rationale, source_evidence=x.source_evidence,
            evidence_request=x.evidence_request,
            created_at=x.created_at,
        ) for x in value.proposals],
        decisions=[DecisionRecord(
            id=x.id, proposal_id=x.proposal_id, proposal_revision=x.proposal_revision,
            decision=x.decision, version_id=x.version_id, created_at=x.created_at,
        ) for x in value.decisions],
        versions=[VersionRecord(
            id=x.id, version_number=x.version_number, version_name=x.version_name,
            parent_version_id=x.parent_version_id, content=x.content, created_at=x.created_at,
        ) for x in value.versions],
        exports=[ExportRecord(id=x.id, version_id=x.version_id,
                              content_type=x.content_type, size_bytes=x.size_bytes,
                              created_at=x.created_at) for x in value.exports],
        latest_event_sequence=value.events[-1].sequence if value.events else 0,
    )


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    user: UserContext = Depends(get_current_user),
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    before: str | None = None,
    repository=Depends(get_workflow_repository),
):
    try:
        items, cursor = await repository.list_runs(user.subject, limit=limit, before=before)
    except ResourceNotFoundError as exc:
        _not_found(exc)
    return RunListResponse(items=[_run(item) for item in items], next_cursor=cursor)


@router.post("/runs", response_model=RunSnapshotResponse, status_code=201)
async def create_run(user: UserContext = Depends(get_current_user),
                     orchestrator=Depends(get_tailoring_orchestrator)):
    run = await orchestrator.create_run(user.subject)
    return _snapshot(await orchestrator.repository.load_run(user.subject, run.id))


@router.get("/runs/{run_id}", response_model=RunSnapshotResponse)
async def get_run(run_id: str, user: UserContext = Depends(get_current_user),
                  repository=Depends(get_workflow_repository)):
    try:
        return _snapshot(await repository.load_run(user.subject, run_id))
    except ResourceNotFoundError as exc:
        _not_found(exc)


@router.post("/runs/{run_id}/resume", response_model=RunSnapshotResponse)
async def submit_resume(run_id: str, file: UploadFile = File(...),
                        user: UserContext = Depends(get_current_user),
                        orchestrator=Depends(get_tailoring_orchestrator)):
    from ...config import get_settings

    settings = get_settings()
    content = await file.read(settings.max_file_size + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Resume file is empty")
    if len(content) > settings.max_file_size:
        raise HTTPException(status_code=413, detail="Resume file is too large")
    extension = (file.filename or "").lower().rsplit(".", 1)[-1]
    allowed_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if extension not in allowed_types or file.content_type != allowed_types[extension]:
        raise HTTPException(status_code=400, detail="Resume must be a PDF or DOCX with matching content type")
    signatures = {"pdf": b"%PDF-", "docx": b"PK\x03\x04"}
    if not content.startswith(signatures[extension]):
        raise HTTPException(status_code=400, detail="Resume content does not match its file type")
    try:
        await orchestrator.submit_resume(user.subject, run_id, file.filename or "resume", content)
        return _snapshot(await orchestrator.repository.load_run(user.subject, run_id))
    except ResourceNotFoundError as exc:
        _not_found(exc)
    except StaleRevisionError as exc:
        _conflict(exc)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/runs/{run_id}/job-description", response_model=RunSnapshotResponse)
async def submit_jd(run_id: str, request: JobDescriptionRequest,
                    user: UserContext = Depends(get_current_user),
                    orchestrator=Depends(get_tailoring_orchestrator)):
    try:
        await orchestrator.submit_job_description(user.subject, run_id, request.content)
        return _snapshot(await orchestrator.repository.load_run(user.subject, run_id))
    except ResourceNotFoundError as exc:
        _not_found(exc)
    except StaleRevisionError as exc:
        _conflict(exc)


@router.post("/runs/{run_id}/messages", response_model=RunSnapshotResponse)
async def send_message(run_id: str, request: MessageRequest,
                       user: UserContext = Depends(get_current_user),
                       orchestrator=Depends(get_tailoring_orchestrator)):
    try:
        await orchestrator.send_message(user.subject, run_id, request.content)
        return _snapshot(await orchestrator.repository.load_run(user.subject, run_id))
    except ResourceNotFoundError as exc:
        _not_found(exc)


@router.post("/runs/{run_id}/evidence", response_model=RunSnapshotResponse)
async def record_evidence(run_id: str, request: EvidenceRequest,
                          user: UserContext = Depends(get_current_user),
                          orchestrator=Depends(get_tailoring_orchestrator)):
    try:
        await orchestrator.record_user_evidence(user.subject, run_id, request.content)
        await orchestrator.repository.append_event(user.subject, run_id, "snapshot_changed", {})
        return _snapshot(await orchestrator.repository.load_run(user.subject, run_id))
    except ResourceNotFoundError as exc:
        _not_found(exc)


@router.post("/runs/{run_id}/proposals/{proposal_id}/decisions",
             response_model=RunSnapshotResponse)
async def decide(run_id: str, proposal_id: str, request: ProposalDecisionRequest,
                 user: UserContext = Depends(get_current_user),
                 orchestrator=Depends(get_tailoring_orchestrator)):
    try:
        await orchestrator.decide_proposal(
            user.subject, run_id, proposal_id, **request.model_dump()
        )
        return _snapshot(await orchestrator.repository.load_run(user.subject, run_id))
    except ResourceNotFoundError as exc:
        _not_found(exc)
    except ValueError as exc:
        _conflict(exc)


@router.get("/runs/{run_id}/versions/{version_id}", response_model=VersionRecord)
async def get_version(run_id: str, version_id: str,
                      user: UserContext = Depends(get_current_user),
                      repository=Depends(get_workflow_repository)):
    try:
        x = await repository.get_version(user.subject, run_id, version_id)
        return VersionRecord(id=x.id, version_number=x.version_number,
                             version_name=x.version_name, parent_version_id=x.parent_version_id,
                             content=x.content, created_at=x.created_at)
    except ResourceNotFoundError as exc:
        _not_found(exc)
    except StaleRevisionError as exc:
        _conflict(exc)


@router.post("/runs/{run_id}/versions/{version_id}/restore", response_model=RunSnapshotResponse)
async def restore(run_id: str, version_id: str, request: RestoreVersionRequest,
                  user: UserContext = Depends(get_current_user),
                  orchestrator=Depends(get_tailoring_orchestrator)):
    try:
        await orchestrator.restore_version(
            user.subject, run_id, version_id,
            idempotency_key=request.idempotency_key,
        )
        return _snapshot(await orchestrator.repository.load_run(user.subject, run_id))
    except ResourceNotFoundError as exc:
        _not_found(exc)
    except StaleRevisionError as exc:
        _conflict(exc)


@router.post("/runs/{run_id}/versions/{version_id}/exports", response_model=ExportRecord)
async def create_export(run_id: str, version_id: str, request: CreateExportRequest,
                        user: UserContext = Depends(get_current_user),
                        orchestrator=Depends(get_tailoring_orchestrator),
                        storage=Depends(get_export_storage_service)):
    try:
        x = await orchestrator.create_export(
            user.subject, run_id, version_id, request.format, storage,
            idempotency_key=request.idempotency_key,
        )
        return ExportRecord(id=x.id, version_id=x.version_id, content_type=x.content_type,
                            size_bytes=x.size_bytes, created_at=x.created_at)
    except ResourceNotFoundError as exc:
        _not_found(exc)
    except StaleRevisionError as exc:
        _conflict(exc)


@router.get("/runs/{run_id}/exports/{export_id}/download")
async def download(run_id: str, export_id: str,
                   user: UserContext = Depends(get_current_user),
                   repository=Depends(get_workflow_repository),
                   storage=Depends(get_object_storage)):
    try:
        record = await repository.get_export(user.subject, run_id, export_id)
        content = await storage.get(user.subject, record.storage_key)
    except (ResourceNotFoundError, ValueError) as exc:
        _not_found(exc)
    suffix = "pdf" if record.content_type == "application/pdf" else "docx"
    return Response(content, media_type=record.content_type, headers={
        "Content-Disposition": f'attachment; filename="resume-{record.version_id}.{suffix}"'
    })


@router.get("/runs/{run_id}/events")
async def events(run_id: str, after: Annotated[int, Query(ge=0)] = 0,
                 user: UserContext = Depends(get_current_user),
                 repository=Depends(get_workflow_repository)):
    try:
        records = await repository.events_after(user.subject, run_id, after)
    except ResourceNotFoundError as exc:
        _not_found(exc)

    async def stream():
        for item in records:
            data = json.dumps({"type": item.event_type, "sequence": item.sequence})
            yield f"id: {item.sequence}\nevent: snapshot\ndata: {data}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache", "X-Accel-Buffering": "no"
    })
