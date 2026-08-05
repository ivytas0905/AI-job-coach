"""Adapters between JSON-shaped tool calls and resume application use cases."""

from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..application.use_cases.analyze_jd import AnalyzeJDUseCase
from ..application.use_cases.export_resume import ExportResumeUseCase
from ..application.use_cases.parse_resume import ParseResumeUseCase
from ..application.use_cases.tailor_resume import TailorResumeUseCase
from ..application.ports.retrieval import EvidenceRetriever
from ..domain.models import (
    BulletPoint,
    Education,
    Experience,
    JobDescription,
    KeywordWeight,
    MasterResume,
    PersonalInfo,
    Resume,
    Skill,
)
from ..tool_registry import ToolContext, ToolEffect, ToolRegistry, ToolSpec


class ParseResumeInput(BaseModel):
    filename: str = Field(min_length=1)
    content: bytes = Field(min_length=1)


class ParseResumeResult(BaseModel):
    resume: dict[str, Any]
    source_evidence: list[str]


class AnalyzeJDInput(BaseModel):
    text: str = Field(min_length=50)


class AnalyzeJDResult(BaseModel):
    analysis: dict[str, Any]
    source_evidence: list[str]


class TailorResumeInput(BaseModel):
    master_resume: dict[str, Any]
    job_description: dict[str, Any]


class ProposalItem(BaseModel):
    affected_content: str
    suggested_replacement: str
    jd_reason: str
    source_evidence: list[str]
    evidence_request: str | None = None


class TailorResumeResult(BaseModel):
    tailored_resume: dict[str, Any]
    proposals: list[ProposalItem]


class ExportResumeInput(BaseModel):
    resume: dict[str, Any]
    format: Literal["pdf", "docx"]
    template: str = "professional"


class ExportResumeResult(BaseModel):
    content: bytes
    content_type: str


class RetrieveEvidenceInput(BaseModel):
    query: str = Field(min_length=2)
    top_k: int = Field(default=5, ge=1, le=10)


class EvidenceItem(BaseModel):
    content: str
    source_type: str
    source_id: str
    score: float
    metadata: dict[str, Any]


class RetrieveEvidenceResult(BaseModel):
    items: list[EvidenceItem]


def build_resume_tool_registry(
    *,
    parse_resume: ParseResumeUseCase,
    analyze_jd: AnalyzeJDUseCase,
    tailor_resume: TailorResumeUseCase,
    export_resume: ExportResumeUseCase,
    evidence_retriever: EvidenceRetriever,
) -> ToolRegistry:
    async def parse(arguments: ParseResumeInput, context: ToolContext) -> ParseResumeResult:
        resume = await parse_resume.execute(arguments.content, arguments.filename)
        if resume.raw_text and context.owner and context.run_id:
            await evidence_retriever.index(
                owner=context.owner,
                run_id=context.run_id,
                source_type="resume",
                source_id=arguments.filename,
                content=resume.raw_text,
            )
        return ParseResumeResult(
            resume=asdict(resume),
            source_evidence=[resume.raw_text] if resume.raw_text else [],
        )

    async def analyze(arguments: AnalyzeJDInput, context: ToolContext) -> AnalyzeJDResult:
        jd = await analyze_jd.execute(arguments.text)
        if context.owner and context.run_id:
            source_id = sha256(jd.raw_text.encode()).hexdigest()
            await evidence_retriever.index(
                owner=context.owner,
                run_id=context.run_id,
                source_type="job_description",
                source_id=source_id,
                content=jd.raw_text,
            )
        return AnalyzeJDResult(analysis=asdict(jd), source_evidence=[jd.raw_text])

    async def tailor(arguments: TailorResumeInput, context: ToolContext) -> TailorResumeResult:
        master = _master_resume(arguments.master_resume)
        result = await tailor_resume.execute(
            master,
            _job_description(arguments.job_description),
        )
        proposals = [
            ProposalItem(
                affected_content=item.original_text,
                suggested_replacement=item.optimized_text,
                jd_reason="; ".join(item.improvements),
                source_evidence=item.source_evidence,
                evidence_request=item.evidence_request,
            )
            for item in result.selected_bullet_optimizations
        ]
        return TailorResumeResult(
            tailored_resume=asdict(_exportable_resume(master, result)),
            proposals=proposals,
        )

    async def export(arguments: ExportResumeInput, context: ToolContext) -> ExportResumeResult:
        content = export_resume.execute(
            _resume(arguments.resume),
            "word" if arguments.format == "docx" else "pdf",
            arguments.template,
        )
        media_type = (
            "application/pdf"
            if arguments.format == "pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        return ExportResumeResult(content=content, content_type=media_type)

    async def retrieve(
        arguments: RetrieveEvidenceInput, context: ToolContext
    ) -> RetrieveEvidenceResult:
        if not context.owner or not context.run_id:
            raise RuntimeError("Authenticated owner and run are required for evidence retrieval")
        matches = await evidence_retriever.retrieve(
            arguments.query, owner=context.owner, run_id=context.run_id,
            top_k=arguments.top_k,
        )
        return RetrieveEvidenceResult(items=[EvidenceItem(**item) for item in matches])

    return ToolRegistry(
        [
            ToolSpec("parse_resume", ParseResumeInput, ParseResumeResult, ToolEffect.READ,
                     {"awaiting_resume"}, parse),
            ToolSpec("analyze_jd", AnalyzeJDInput, AnalyzeJDResult, ToolEffect.READ,
                     {"awaiting_jd", "ready"}, analyze),
            ToolSpec("propose_tailoring", TailorResumeInput, TailorResumeResult,
                     ToolEffect.PROPOSAL, {"analyzing", "proposal_ready"}, tailor),
            ToolSpec("export_approved_resume", ExportResumeInput, ExportResumeResult,
                     ToolEffect.MUTATION, {"approved"}, export),
            ToolSpec("retrieve_evidence", RetrieveEvidenceInput, RetrieveEvidenceResult,
                     ToolEffect.READ,
                     {"analyzing", "proposal_ready"},
                     retrieve),
        ]
    )


def _personal_info(data: dict[str, Any] | None) -> PersonalInfo | None:
    return PersonalInfo(**data) if data else None


def _experiences(items: list[dict[str, Any]]) -> list[Experience]:
    return [
        Experience(
            **{
                **item,
                "bullets": [BulletPoint(**bullet) for bullet in item.get("bullets", [])],
            }
        )
        for item in items
    ]


def _resume(data: dict[str, Any]) -> Resume:
    return Resume(
        personal_info=_personal_info(data.get("personal_info")),
        experiences=_experiences(data.get("experiences", [])),
        education=[Education(**item) for item in data.get("education", [])],
        skills=[Skill(**item) for item in data.get("skills", [])],
        summary=data.get("summary"),
        target_job=data.get("target_job"),
        raw_text=data.get("raw_text"),
        sections=data.get("sections", {}),
    )


def _master_resume(data: dict[str, Any]) -> MasterResume:
    fields = dict(
        user_id=data.get("user_id"),
        personal_info=_personal_info(data.get("personal_info")),
        experiences=_experiences(data.get("experiences", [])),
        education=[Education(**item) for item in data.get("education", [])],
        skills=[Skill(**item) for item in data.get("skills", [])],
    )
    if data.get("id"):
        fields["id"] = data["id"]
    return MasterResume(**fields)


def _job_description(data: dict[str, Any]) -> JobDescription:
    return JobDescription(
        **{
            **data,
            "keywords": [KeywordWeight(**item) for item in data.get("keywords", [])],
        }
    )


def _exportable_resume(master: MasterResume, tailored: Any) -> Resume:
    """Materialize the selected proposal as a standalone, export-ready snapshot."""
    optimizations = {
        item.bullet_id: item.optimized_text
        for item in tailored.selected_bullet_optimizations
    }
    experiences = []
    for source in master.experiences:
        if source.id not in tailored.selected_experience_ids:
            continue
        experience = deepcopy(source)
        selected_bullets = [
            deepcopy(bullet)
            for bullet in source.bullets
            if bullet.id in optimizations
        ]
        for bullet in selected_bullets:
            bullet.text = optimizations[bullet.id]
        experience.bullets = selected_bullets
        if selected_bullets:
            experience.description = "\n".join(bullet.text for bullet in selected_bullets)
        experiences.append(experience)

    education_ids = set(tailored.selected_education_ids)
    selected_skills = set(tailored.selected_skills)
    return Resume(
        personal_info=deepcopy(tailored.personal_info),
        experiences=experiences,
        education=[deepcopy(item) for item in master.education if item.id in education_ids],
        skills=[deepcopy(item) for item in master.skills if item.name in selected_skills],
    )
