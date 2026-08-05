"""Owner-scoped persistence for resume tailoring workflows."""

from dataclasses import dataclass
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import (
    AgentMessageModel,
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
    messages: list[AgentMessageModel]
    proposals: list[ProposalModel]
    decisions: list[ProposalDecisionModel]
    versions: list[ResumeVersionModel]
    exports: list[ExportModel]


class WorkflowRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def _owned_run(
        self, session: AsyncSession, owner: str, run_id: str
    ) -> TailoringRunModel:
        run = await session.scalar(
            select(TailoringRunModel).where(
                TailoringRunModel.id == run_id,
                TailoringRunModel.user_id == owner,
            )
        )
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

    async def append_message(
        self, owner: str, run_id: str, role: str, content: str
    ) -> AgentMessageModel:
        async with self.session_factory() as session, session.begin():
            await self._owned_run(session, owner, run_id)
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

    async def create_proposal(
        self,
        owner: str,
        run_id: str,
        original_text: str,
        suggested_text: str,
        rationale: str,
        source_evidence: dict,
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
    ) -> DecisionResult:
        if decision not in {"accepted", "rejected", "revision_requested"}:
            raise ValueError("Unsupported proposal decision")
        async with self.session_factory() as session, session.begin():
            proposal = await session.scalar(
                select(ProposalModel).where(
                    ProposalModel.id == proposal_id,
                    ProposalModel.user_id == owner,
                )
            )
            if proposal is None:
                raise ResourceNotFoundError("Proposal not found")
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
            session.add(record)
            await session.flush()
            return DecisionResult(decision=record, version=None)

    async def create_version(
        self,
        owner: str,
        run_id: str,
        name: str,
        content: dict,
        *,
        parent_version_id: str | None = None,
    ) -> ResumeVersionModel:
        async with self.session_factory() as session, session.begin():
            run = await self._owned_run(session, owner, run_id)
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
            )
            session.add(version)
            await session.flush()
            run.current_version_id = version.id
            run.revision += 1
            return version

    async def restore_version(
        self, owner: str, run_id: str, version_id: str
    ) -> ResumeVersionModel:
        async with self.session_factory() as session:
            await self._owned_run(session, owner, run_id)
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
    ) -> ExportModel:
        async with self.session_factory() as session, session.begin():
            if not storage_key.startswith(f"{owner}/"):
                raise ResourceNotFoundError("Stored export not found")
            await self._owned_run(session, owner, run_id)
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
            return RunSnapshot(run, messages, proposals, decisions, versions, exports)
