from dataclasses import dataclass

import pytest

from agent_service.application.use_cases.build_resume import (
    BuildContactInput,
    BuildEducationInput,
    BuildExperienceInput,
    BuildResumeInput,
    BuildResumeUseCase,
)


@dataclass
class FakeEnhancer:
    calls: int = 0

    async def enhance_resume(self, resume):
        self.calls += 1
        resume.summary = "Enhanced summary"
        return resume


def build_input(*, enhance: bool = False) -> BuildResumeInput:
    return BuildResumeInput(
        contact=BuildContactInput("Ada Lovelace", "ada@example.com", "123"),
        experiences=(
            BuildExperienceInput("Engineer", "Analytical Engines", "1842"),
        ),
        education=(BuildEducationInput("Mathematics", "University", "1830"),),
        skills=("Python",),
        summary="Builder",
        target_job="Staff Engineer",
        enhance_with_ai=enhance,
    )


@pytest.mark.asyncio
async def test_build_maps_application_input_without_enhancement():
    enhancer = FakeEnhancer()

    result = await BuildResumeUseCase(enhancer=enhancer).execute(build_input())

    assert result.resume.personal_info.fullname == "Ada Lovelace"
    assert result.resume.experiences[0].title == "Engineer"
    assert result.resume.skills[0].name == "Python"
    assert result.resume.target_job == "Staff Engineer"
    assert enhancer.calls == 0


@pytest.mark.asyncio
async def test_build_uses_injected_enhancer_when_requested():
    enhancer = FakeEnhancer()

    result = await BuildResumeUseCase(enhancer=enhancer).execute(
        build_input(enhance=True)
    )

    assert result.resume.summary == "Enhanced summary"
    assert enhancer.calls == 1


@pytest.mark.asyncio
async def test_build_rejects_missing_enhancer_when_requested():
    with pytest.raises(RuntimeError, match="enhancement capability is not configured"):
        await BuildResumeUseCase().execute(build_input(enhance=True))
