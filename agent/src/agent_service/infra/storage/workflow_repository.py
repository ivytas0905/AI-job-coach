"""Owner-scoped persistence for resume tailoring workflows."""

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import (
    AgentMessageModel,
    AgentEventModel,
    ExportModel,
    JDAnalysisModel,
    MasterResumeModel,
    ProposalDecisionModel,
    ProposalModel,
    ResumeVersionModel,
    TailoringRunModel,
)


class ResourceNotFoundError(LookupError):
    """Returned for absent and foreign resources to avoid ownership disclosure."""


class StaleRevisionError(ValueError):
    pass


@dataclass(frozen=True)
class DecisionResult:
    decision: ProposalDecisionModel
    version: ResumeVersionModel | None


@dataclass(frozen=True)
class RunSnapshot:
    run: TailoringRunModel
    master_resume: MasterResumeModel | None
    job_description: JDAnalysisModel | None
    messages: list[AgentMessageModel]
    proposals: list[ProposalModel]
    decisions: list[ProposalDecisionModel]
    versions: list[ResumeVersionModel]
    exports: list[ExportModel]
    events: list[AgentEventModel]


class WorkflowRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def _owned_run(
        self, session: AsyncSession, owner: str, run_id: str, *, for_update: bool = False
    ) -> TailoringRunModel:
        statement = select(TailoringRunModel).where(
            TailoringRunModel.id == run_id,
            TailoringRunModel.user_id == owner,
        )
        if for_update:
            statement = statement.with_for_update()
        run = await session.scalar(statement)
        if run is None:
            raise ResourceNotFoundError("Tailoring run not found")
        return run

    async def create_run(
        self,
        owner: str,
        *,
        provider: str,
        model: str,
        master_resume_id: str | None = None,
        jd_analysis_id: str | None = None,
    ) -> TailoringRunModel:
        async with self.session_factory() as session, session.begin():
            if master_resume_id is not None:
                master = await session.scalar(
                    select(MasterResumeModel.id).where(
                        MasterResumeModel.id == master_resume_id,
                        MasterResumeModel.user_id == owner,
                    )
                )
                if master is None:
                    raise ResourceNotFoundError("Master resume not found")
            if jd_analysis_id is not None:
                job_description = await session.scalar(
                    select(JDAnalysisModel.id).where(
                        JDAnalysisModel.id == jd_analysis_id,
                        JDAnalysisModel.user_id == owner,
                    )
                )
                if job_description is None:
                    raise ResourceNotFoundError("Job description not found")
            run = TailoringRunModel(
                user_id=owner,
                provider=provider,
                model=model,
                master_resume_id=master_resume_id,
                jd_analysis_id=jd_analysis_id,
            )
            session.add(run)
            await session.flush()
            return run

    async def list_runs(self, owner: str, *, limit: int = 20, before: str | None = None):
        async with self.session_factory() as session:
            statement = select(TailoringRunModel).where(TailoringRunModel.user_id == owner)
            if before:
                cursor = await session.execute(
                    select(TailoringRunModel.created_at, TailoringRunModel.id).where(
                        TailoringRunModel.id == before,
                        TailoringRunModel.user_id == owner,
                    )
                )
                cursor_row = cursor.one_or_none()
                if cursor_row is None:
                    raise ResourceNotFoundError("Run cursor not found")
                cursor_created_at, cursor_id = cursor_row
                statement = statement.where(or_(
                    TailoringRunModel.created_at < cursor_created_at,
                    and_(TailoringRunModel.created_at == cursor_created_at,
                         TailoringRunModel.id < cursor_id),
                ))
            rows = await session.scalars(
                statement.order_by(
                    desc(TailoringRunModel.created_at), desc(TailoringRunModel.id)
                ).limit(limit + 1)
            )
            items = list(rows.all())
            return items[:limit], (items[limit - 1].id if len(items) > limit else None)

    async def attach_master_resume(
        self, owner: str, run_id: str, *, filename: str, parsed_data: dict
    ) -> TailoringRunModel:
        async with self.session_factory() as session, session.begin():
            run = await self._owned_run(session, owner, run_id)
            if run.state != "awaiting_resume":
                raise StaleRevisionError("Run is not awaiting a resume")
            master = MasterResumeModel(
                user_id=owner, filename=filename, parsed_data=parsed_data
            )
            session.add(master)
            await session.flush()
            run.master_resume_id = master.id
            run.state = "awaiting_jd"
            run.revision += 1
            return run

    async def attach_job_description(
        self, owner: str, run_id: str, *, raw_text: str, analysis: dict, jd_hash: str
    ) -> TailoringRunModel:
        async with self.session_factory() as session, session.begin():
            run = await self._owned_run(session, owner, run_id)
            if run.state != "awaiting_jd":
                raise StaleRevisionError("Run is not awaiting a job description")
            owned_hash = sha256(f"{owner}\0{jd_hash}".encode()).hexdigest()
            job = await session.scalar(select(JDAnalysisModel).where(
                JDAnalysisModel.user_id == owner, JDAnalysisModel.jd_hash == owned_hash
            ))
            if job is None:
                job = JDAnalysisModel(
                    user_id=owner,
                    company=analysis.get("company"),
                    job_title=analysis.get("job_title") or "Target role",
                    raw_text=raw_text,
                    jd_hash=owned_hash,
                    analysis_result=analysis,
                )
                session.add(job)
                await session.flush()
            run.jd_analysis_id = job.id
            run.state = "analyzing"
            run.revision += 1
            return run

    async def events_after(self, owner: str, run_id: str, sequence: int):
        async with self.session_factory() as session:
            await self._owned_run(session, owner, run_id)
            rows = await session.scalars(
                select(AgentEventModel).where(
                    AgentEventModel.run_id == run_id,
                    AgentEventModel.user_id == owner,
                    AgentEventModel.sequence > sequence,
                ).order_by(AgentEventModel.sequence)
            )
            return list(rows.all())

    async def get_version(self, owner: str, run_id: str, version_id: str):
        async with self.session_factory() as session:
            await self._owned_run(session, owner, run_id)
            version = await session.scalar(select(ResumeVersionModel).where(
                ResumeVersionModel.id == version_id,
                ResumeVersionModel.run_id == run_id,
                ResumeVersionModel.user_id == owner,
            ))
            if version is None:
                raise ResourceNotFoundError("Resume version not found")
            return version

    async def get_export(self, owner: str, run_id: str, export_id: str):
        async with self.session_factory() as session:
            await self._owned_run(session, owner, run_id)
            export = await session.scalar(select(ExportModel).where(
                ExportModel.id == export_id,
                ExportModel.run_id == run_id,
                ExportModel.user_id == owner,
            ))
            if export is None:
                raise ResourceNotFoundError("Export not found")
            return export

    async def get_export_by_idempotency_key(
        self, owner: str, run_id: str, idempotency_key: str
    ):
        async with self.session_factory() as session:
            await self._owned_run(session, owner, run_id)
            return await session.scalar(select(ExportModel).where(
                ExportModel.run_id == run_id,
                ExportModel.user_id == owner,
                ExportModel.idempotency_key == idempotency_key,
            ))

    async def transition_run(
        self, owner: str, run_id: str, *, expected_state: str, new_state: str
    ) -> TailoringRunModel:
        async with self.session_factory() as session, session.begin():
            result = await session.execute(
                update(TailoringRunModel)
                .where(
                    TailoringRunModel.id == run_id,
                    TailoringRunModel.user_id == owner,
                    TailoringRunModel.state == expected_state,
                )
                .values(state=new_state, revision=TailoringRunModel.revision + 1)
            )
            if result.rowcount != 1:
                run = await self._owned_run(session, owner, run_id)
                raise StaleRevisionError(f"Run is in state {run.state}, expected {expected_state}")
            return await self._owned_run(session, owner, run_id)

    async def append_message(
        self, owner: str, run_id: str, role: str, content: str
    ) -> AgentMessageModel:
        async with self.session_factory() as session, session.begin():
            await self._owned_run(session, owner, run_id, for_update=True)
            last_sequence = await session.scalar(
                select(func.max(AgentMessageModel.sequence)).where(
                    AgentMessageModel.run_id == run_id,
                    AgentMessageModel.user_id == owner,
                )
            )
            message = AgentMessageModel(
                run_id=run_id,
                user_id=owner,
                sequence=(last_sequence or 0) + 1,
                role=role,
                content=content,
            )
            session.add(message)
            await session.flush()
            return message

    async def append_event(self, owner: str, run_id: str, event_type: str, payload: dict):
        async with self.session_factory() as session, session.begin():
            await self._owned_run(session, owner, run_id, for_update=True)
            last = await session.scalar(select(func.max(AgentEventModel.sequence)).where(
                AgentEventModel.run_id == run_id, AgentEventModel.user_id == owner
            ))
            event = AgentEventModel(run_id=run_id, user_id=owner, sequence=(last or 0) + 1,
                                    event_type=event_type, payload=payload)
            session.add(event)
            await session.flush()
            return event

    async def create_proposal(
        self,
        owner: str,
        run_id: str,
        original_text: str,
        suggested_text: str,
        rationale: str,
        source_evidence: dict,
        evidence_request: str | None = None,
    ) -> ProposalModel:
        async with self.session_factory() as session, session.begin():
            await self._owned_run(session, owner, run_id)
            proposal = ProposalModel(
                run_id=run_id,
                user_id=owner,
                original_text=original_text,
                suggested_text=suggested_text,
                rationale=rationale,
                source_evidence=source_evidence,
                evidence_request=evidence_request,
            )
            session.add(proposal)
            await session.flush()
            return proposal

    async def decide_proposal(
        self,
        owner: str,
        proposal_id: str,
        *,
        decision: Literal["accepted", "rejected", "revision_requested"],
        expected_revision: int,
        idempotency_key: str,
        version_name: str | None = None,
    ) -> DecisionResult:
        if decision not in {"accepted", "rejected", "revision_requested"}:
            raise ValueError("Unsupported proposal decision")
        async with self.session_factory() as session, session.begin():
            proposal = await session.scalar(
                select(ProposalModel).where(
                    ProposalModel.id == proposal_id,
                    ProposalModel.user_id == owner,
                ).with_for_update()
            )
            if proposal is None:
                raise ResourceNotFoundError("Proposal not found")
            existing = await session.scalar(
                select(ProposalDecisionModel).where(
                    ProposalDecisionModel.user_id == owner,
                    ProposalDecisionModel.run_id == proposal.run_id,
                    ProposalDecisionModel.idempotency_key == idempotency_key,
                )
            )
            if existing is not None:
                if existing.proposal_id != proposal_id or existing.decision != decision:
                    raise StaleRevisionError("Idempotency key was used for another decision")
                version = await session.get(ResumeVersionModel, existing.version_id) if existing.version_id else None
                return DecisionResult(existing, version)
            if proposal.revision != expected_revision or proposal.status != "pending":
                raise StaleRevisionError("Proposal revision is no longer current")
            record = ProposalDecisionModel(
                proposal_id=proposal.id,
                run_id=proposal.run_id,
                user_id=owner,
                proposal_revision=proposal.revision,
                decision=decision,
                idempotency_key=idempotency_key,
            )
            proposal.status = decision
            version = None
            if decision == "accepted":
                run = await self._owned_run(session, owner, proposal.run_id)
                if run.master_resume_id is None:
                    raise ResourceNotFoundError("Run has no master resume")
                master = await session.scalar(select(MasterResumeModel).where(
                    MasterResumeModel.id == run.master_resume_id,
                    MasterResumeModel.user_id == owner,
                ))
                if master is None:
                    raise ResourceNotFoundError("Run has no master resume")
                last_number = await session.scalar(
                    select(func.max(ResumeVersionModel.version_number)).where(
                        ResumeVersionModel.run_id == run.id,
                        ResumeVersionModel.user_id == owner,
                    )
                )
                version_content = _replace_text(
                    master.parsed_data, proposal.original_text, proposal.suggested_text
                )
                if version_content == master.parsed_data:
                    raise StaleRevisionError(
                        "Approved proposal no longer matches the master resume"
                    )
                version = ResumeVersionModel(
                    user_id=owner, run_id=run.id, master_resume_id=run.master_resume_id,
                    version_number=(last_number or 0) + 1,
                    version_name=version_name or f"Tailored version {(last_number or 0) + 1}",
                    content=version_content, status="finalized",
                )
                session.add(version)
                await session.flush()
                record.version_id = version.id
                run.current_version_id = version.id
                run.state = "version_ready"
                run.revision += 1
            session.add(record)
            await session.flush()
            return DecisionResult(decision=record, version=version)

    async def create_version(
        self,
        owner: str,
        run_id: str,
        name: str,
        content: dict,
        *,
        parent_version_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> ResumeVersionModel:
        async with self.session_factory() as session, session.begin():
            run = await self._owned_run(session, owner, run_id, for_update=True)
            if idempotency_key:
                replay = await session.scalar(select(ResumeVersionModel).where(
                    ResumeVersionModel.run_id == run_id,
                    ResumeVersionModel.user_id == owner,
                    ResumeVersionModel.idempotency_key == idempotency_key,
                ))
                if replay is not None:
                    if replay.parent_version_id != parent_version_id:
                        raise StaleRevisionError("Idempotency key was used for another version")
                    return replay
            if run.master_resume_id is None:
                raise ResourceNotFoundError("Run has no master resume")
            if parent_version_id is not None:
                parent = await session.scalar(
                    select(ResumeVersionModel.id).where(
                        ResumeVersionModel.id == parent_version_id,
                        ResumeVersionModel.run_id == run_id,
                        ResumeVersionModel.user_id == owner,
                    )
                )
                if parent is None:
                    raise ResourceNotFoundError("Parent resume version not found")
            last_number = await session.scalar(
                select(func.max(ResumeVersionModel.version_number)).where(
                    ResumeVersionModel.run_id == run_id,
                    ResumeVersionModel.user_id == owner,
                )
            )
            version = ResumeVersionModel(
                user_id=owner,
                run_id=run_id,
                master_resume_id=run.master_resume_id,
                parent_version_id=parent_version_id,
                version_number=(last_number or 0) + 1,
                version_name=name,
                content=content,
                status="finalized",
                idempotency_key=idempotency_key,
            )
            session.add(version)
            await session.flush()
            run.current_version_id = version.id
            run.revision += 1
            return version

    async def restore_version(
        self, owner: str, run_id: str, version_id: str, *, idempotency_key: str
    ) -> ResumeVersionModel:
        async with self.session_factory() as session:
            await self._owned_run(session, owner, run_id, for_update=True)
            source = await session.scalar(
                select(ResumeVersionModel).where(
                    ResumeVersionModel.id == version_id,
                    ResumeVersionModel.run_id == run_id,
                    ResumeVersionModel.user_id == owner,
                )
            )
            if source is None:
                raise ResourceNotFoundError("Resume version not found")
            source_name = source.version_name
            source_content = dict(source.content)
        return await self.create_version(
            owner,
            run_id,
            f"Restored: {source_name}",
            source_content,
            parent_version_id=version_id,
            idempotency_key=idempotency_key,
        )

    async def create_export(
        self,
        *,
        owner: str,
        run_id: str,
        version_id: str,
        storage_key: str,
        content_type: str,
        size_bytes: int,
        idempotency_key: str | None = None,
    ) -> ExportModel:
        async with self.session_factory() as session, session.begin():
            if not storage_key.startswith(f"{owner}/"):
                raise ResourceNotFoundError("Stored export not found")
            await self._owned_run(session, owner, run_id, for_update=True)
            if idempotency_key:
                replay = await session.scalar(select(ExportModel).where(
                    ExportModel.run_id == run_id,
                    ExportModel.user_id == owner,
                    ExportModel.idempotency_key == idempotency_key,
                ))
                if replay is not None:
                    if replay.version_id != version_id or replay.content_type != content_type:
                        raise StaleRevisionError("Idempotency key was used for another export")
                    return replay
            version = await session.scalar(
                select(ResumeVersionModel.id).where(
                    ResumeVersionModel.id == version_id,
                    ResumeVersionModel.run_id == run_id,
                    ResumeVersionModel.user_id == owner,
                )
            )
            if version is None:
                raise ResourceNotFoundError("Resume version not found")
            export = ExportModel(
                user_id=owner,
                run_id=run_id,
                version_id=version_id,
                storage_key=storage_key,
                content_type=content_type,
                size_bytes=size_bytes,
                idempotency_key=idempotency_key,
            )
            session.add(export)
            await session.flush()
            return export

    async def load_run(self, owner: str, run_id: str) -> RunSnapshot:
        async with self.session_factory() as session:
            run = await self._owned_run(session, owner, run_id)

            async def rows(model, *order_by):
                result = await session.scalars(
                    select(model)
                    .where(model.run_id == run_id, model.user_id == owner)
                    .order_by(*order_by)
                )
                return list(result.all())

            messages = await rows(AgentMessageModel, AgentMessageModel.sequence)
            proposals = await rows(ProposalModel, ProposalModel.created_at)
            decisions = await rows(ProposalDecisionModel, ProposalDecisionModel.created_at)
            versions = await rows(ResumeVersionModel, ResumeVersionModel.version_number)
            exports = await rows(ExportModel, ExportModel.created_at)
            events = await rows(AgentEventModel, AgentEventModel.sequence)
            master_resume = (await session.scalar(select(MasterResumeModel).where(
                MasterResumeModel.id == run.master_resume_id,
                MasterResumeModel.user_id == owner,
            ))) if run.master_resume_id else None
            job_description = (await session.scalar(select(JDAnalysisModel).where(
                JDAnalysisModel.id == run.jd_analysis_id,
                JDAnalysisModel.user_id == owner,
            ))) if run.jd_analysis_id else None
            return RunSnapshot(run, master_resume, job_description, messages, proposals,
                               decisions, versions, exports, events)


def _replace_text(value, original: str, replacement: str):
    """Return a copied resume payload with the approved exact text substitution."""
    if isinstance(value, dict):
        return {key: _replace_text(item, original, replacement) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_text(item, original, replacement) for item in value]
    if isinstance(value, str):
        return value.replace(original, replacement)
    return value
