"""Build a resume from application-owned input."""

from dataclasses import dataclass
from typing import Protocol

from ...domain.models import Education, Experience, PersonalInfo, Resume, Skill


@dataclass(frozen=True)
class BuildContactInput:
    full_name: str
    email: str
    phone: str
    location: str | None = None
    title: str | None = None


@dataclass(frozen=True)
class BuildExperienceInput:
    position: str
    company: str
    start_date: str
    end_date: str | None = None
    location: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class BuildEducationInput:
    degree: str
    school: str
    start_date: str
    end_date: str | None = None
    location: str | None = None


@dataclass(frozen=True)
class BuildResumeInput:
    contact: BuildContactInput
    experiences: tuple[BuildExperienceInput, ...]
    education: tuple[BuildEducationInput, ...]
    skills: tuple[str, ...]
    summary: str | None = None
    target_job: str | None = None
    enhance_with_ai: bool = False


@dataclass(frozen=True)
class BuildResumeResult:
    resume: Resume


class ResumeEnhancer(Protocol):
    async def enhance_resume(self, resume: Resume) -> Resume: ...


class BuildResumeUseCase:
    def __init__(self, enhancer: ResumeEnhancer | None = None):
        self._enhancer = enhancer

    async def execute(self, request: BuildResumeInput) -> BuildResumeResult:
        resume = Resume(
            personal_info=PersonalInfo(
                fullname=request.contact.full_name,
                email=request.contact.email,
                phone=request.contact.phone,
                location=request.contact.location,
                title=request.contact.title,
            ),
            experiences=[
                Experience(
                    type="work",
                    title=item.position,
                    company=item.company,
                    location=item.location,
                    start_date=item.start_date,
                    end_date=item.end_date,
                    description=item.description or "",
                )
                for item in request.experiences
            ],
            education=[
                Education(
                    degree=item.degree,
                    school=item.school,
                    start_date=item.start_date,
                    end_date=item.end_date,
                    location=item.location,
                )
                for item in request.education
            ],
            skills=[Skill(name=skill) for skill in request.skills],
            summary=request.summary or "",
            target_job=request.target_job,
        )

        if request.enhance_with_ai:
            if self._enhancer is None:
                raise RuntimeError("Resume enhancement capability is not configured")
            resume = await self._enhancer.enhance_resume(resume)

        return BuildResumeResult(resume=resume)
