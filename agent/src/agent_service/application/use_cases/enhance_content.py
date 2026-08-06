"""Application operations for LLM-assisted resume text enhancement."""

from dataclasses import dataclass

from ..ports.llm import LlmMessage, LlmProvider, require_text
from ...domain.models import Resume


@dataclass(frozen=True)
class EnhanceContentInput:
    description: str
    job_title: str | None = None
    company: str | None = None


@dataclass(frozen=True)
class EnhanceSummaryInput:
    summary: str
    target_job: str | None = None
    skills: tuple[str, ...] = ()
    years_of_experience: int | None = None


@dataclass(frozen=True)
class EnhanceContentResult:
    enhanced: str


class EnhanceContentUseCase:
    def __init__(self, llm: LlmProvider):
        self._llm = llm

    async def enhance_experience(
        self, request: EnhanceContentInput
    ) -> EnhanceContentResult:
        description = request.description.strip()
        if not description:
            raise ValueError("Description is required")

        context = "\n".join(
            part
            for part in (
                f"Position: {request.job_title}" if request.job_title else "",
                f"Company: {request.company}" if request.company else "",
            )
            if part
        )
        prompt = f"""You are a professional resume optimization expert. Enhance the following work experience description.

{context}

Original Description:
{description}

Use concise bullet points and strong action verbs. Preserve factual accuracy and never invent numbers, percentages, or timeframes. Return only the enhanced description."""
        result = await self._llm.complete(
            [LlmMessage(role="user", content=prompt)],
            max_tokens=1500,
            temperature=0.7,
        )
        return EnhanceContentResult(require_text(result).strip())


    async def enhance_summary(
        self, request: EnhanceSummaryInput
    ) -> EnhanceContentResult:
        summary = request.summary.strip()
        if not summary:
            raise ValueError("Summary is required")

        context = "\n".join(
            part
            for part in (
                f"Target Position: {request.target_job}" if request.target_job else "",
                f"Key Skills: {', '.join(request.skills[:5])}" if request.skills else "",
                (
                    f"Years of Experience: {request.years_of_experience}"
                    if request.years_of_experience is not None
                    else ""
                ),
            )
            if part
        )
        prompt = f"""You are a professional resume writer. Enhance the following professional summary.

{context}

Original Summary:
{summary}

Keep it ATS-friendly, factual, and concise (3-4 sentences). Return only the enhanced summary as one paragraph."""
        result = await self._llm.complete(
            [LlmMessage(role="user", content=prompt)],
            max_tokens=800,
            temperature=0.6,
        )
        return EnhanceContentResult(require_text(result).strip())


class ResumeContentEnhancer:
    """Applies the text enhancement capability to a complete built resume."""

    def __init__(self, content: EnhanceContentUseCase):
        self._content = content

    async def enhance_resume(self, resume: Resume) -> Resume:
        for experience in resume.experiences:
            if experience.description and experience.description.strip():
                result = await self._content.enhance_experience(
                    EnhanceContentInput(
                        description=experience.description,
                        job_title=experience.title,
                        company=experience.company,
                    )
                )
                experience.description = result.enhanced

        if resume.summary and resume.summary.strip():
            result = await self._content.enhance_summary(
                EnhanceSummaryInput(
                    summary=resume.summary,
                    target_job=resume.target_job,
                    skills=tuple(skill.name for skill in resume.skills if skill.name),
                )
            )
            resume.summary = result.enhanced
        return resume
