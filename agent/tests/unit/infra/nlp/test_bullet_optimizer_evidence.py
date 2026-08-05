import pytest

from agent_service.application.ports.llm import LlmResult
from agent_service.domain.models import BulletPoint, JobDescription, KeywordWeight
from agent_service.infra.nlp.bullet_optimizer import BulletOptimizer


class FakeLlm:
    def __init__(self, text="Increased conversion by 35% using Python"):
        self.text = text

    async def complete(self, messages, **kwargs):
        return LlmResult(
            text=self.text,
            usage={"input_tokens": 1, "output_tokens": 1},
            finish_reason="stop",
        )


async def test_optimizer_does_not_propose_unsupported_metric_and_requests_evidence():
    optimizer = BulletOptimizer(FakeLlm())
    bullet = BulletPoint(id="b-1", text="Improved conversion using Python")
    jd = JobDescription(keywords=[KeywordWeight("Python", 0.9, "required")])

    result = await optimizer.optimize_bullet(bullet, jd)

    assert result.optimized_text == bullet.text
    assert result.source_evidence == [bullet.text]
    assert result.evidence_request is not None
    assert "35%" in result.evidence_request


@pytest.mark.parametrize("metric", ["$3M", "20K", "2x", "1,500", "€ 4.5B"])
async def test_optimizer_rejects_common_unsupported_metric_formats(metric):
    optimizer = BulletOptimizer(FakeLlm(f"Delivered {metric} in measurable impact"))
    bullet = BulletPoint(id="b-1", text="Delivered measurable impact")
    jd = JobDescription()

    result = await optimizer.optimize_bullet(bullet, jd)

    assert result.optimized_text == bullet.text
    assert metric in result.evidence_request


async def test_optimizer_allows_supported_metric_with_equivalent_formatting():
    optimizer = BulletOptimizer(FakeLlm("Processed 1,500 requests"))
    bullet = BulletPoint(id="b-1", text="Processed 1500 requests")

    result = await optimizer.optimize_bullet(bullet, JobDescription())

    assert result.optimized_text == "Processed 1,500 requests"
    assert result.evidence_request is None
