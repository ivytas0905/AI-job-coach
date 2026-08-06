import pytest

from agent_service.application.ports.llm import LlmResult
from agent_service.application.use_cases.enhance_content import (
    EnhanceContentInput,
    EnhanceContentUseCase,
    EnhanceSummaryInput,
    ResumeContentEnhancer,
)
from agent_service.domain.models import Experience, Resume, Skill


class FakeLlm:
    provider_name = "fake"
    model = "fake-model"

    def __init__(self):
        self.calls = []

    async def complete(self, messages, **options):
        self.calls.append((messages, options))
        return LlmResult(text="  Improved content  ", finish_reason="stop")


@pytest.mark.asyncio
async def test_enhance_experience_rejects_blank_content_without_provider_call():
    llm = FakeLlm()

    with pytest.raises(ValueError, match="Description is required"):
        await EnhanceContentUseCase(llm).enhance_experience(
            EnhanceContentInput(description="   ")
        )

    assert llm.calls == []


@pytest.mark.asyncio
async def test_enhance_experience_calls_provider_once_and_trims_result():
    llm = FakeLlm()

    result = await EnhanceContentUseCase(llm).enhance_experience(
        EnhanceContentInput(
            description="Built services", job_title="Engineer", company="Acme"
        )
    )

    assert result.enhanced == "Improved content"
    assert len(llm.calls) == 1
    assert "Built services" in llm.calls[0][0][0].content


@pytest.mark.asyncio
async def test_enhance_summary_rejects_blank_content_without_provider_call():
    llm = FakeLlm()

    with pytest.raises(ValueError, match="Summary is required"):
        await EnhanceContentUseCase(llm).enhance_summary(EnhanceSummaryInput(summary=""))

    assert llm.calls == []


@pytest.mark.asyncio
async def test_resume_enhancer_enhances_nonblank_experience_and_summary():
    llm = FakeLlm()
    resume = Resume(
        experiences=[Experience(title="Engineer", description="Built services")],
        skills=[Skill("Python")],
        summary="Experienced engineer",
        target_job="Staff Engineer",
    )

    result = await ResumeContentEnhancer(EnhanceContentUseCase(llm)).enhance_resume(resume)

    assert result.experiences[0].description == "Improved content"
    assert result.summary == "Improved content"
    assert len(llm.calls) == 2
