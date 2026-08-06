from agent_service.domain.models import BulletOptimization
from agent_service.domain.resume_policies import calculate_ats_score


def test_ats_score_applies_match_metrics_and_keyword_weights():
    optimizations = [
        BulletOptimization("1", "a", "b", ["Added quantifiable metric"], ["x", "y", "z"]),
        BulletOptimization("2", "a", "b", [], []),
    ]
    assert calculate_ats_score(50, optimizations) == 50


def test_ats_score_handles_no_optimizations_and_clamps_range():
    assert calculate_ats_score(50, []) == 30
    assert calculate_ats_score(-20, []) == 0
    assert calculate_ats_score(200, []) == 60
