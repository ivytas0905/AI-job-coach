"""Deterministic resume rules shared by every application entry point."""

from dataclasses import dataclass
import re
from typing import Sequence

from .models import BulletOptimization, JobDescription, MasterResume


def calculate_ats_score(
    match_score: float, optimizations: Sequence[BulletOptimization]
) -> float:
    score = max(0.0, min(float(match_score), 100.0)) * 0.6
    if optimizations:
        metrics_count = sum(
            any("metric" in item.lower() or "quantif" in item.lower() for item in opt.improvements)
            for opt in optimizations
        )
        score += metrics_count / len(optimizations) * 20
        average_keywords = sum(len(opt.keyword_matches) for opt in optimizations) / len(optimizations)
        score += min(average_keywords / 3 * 20, 20)
    return max(0.0, min(score, 100.0))


def select_skills(
    master_resume: MasterResume, jd: JobDescription, *, limit: int = 15
) -> list[str]:
    jd_skills = {name.casefold() for name in jd.required_skills + jd.preferred_skills}
    names = [skill.name for skill in master_resume.skills if skill.name]
    matched = [name for name in names if name.casefold() in jd_skills]
    unmatched = [name for name in names if name.casefold() not in jd_skills]
    return (matched + unmatched)[: max(0, limit)]


_METRIC_PATTERN = re.compile(
    r"(?<![\w.])(?:[$€£¥]\s*)?\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:%|[kmb]|x))?(?!\w)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EvidenceDecision:
    accepted_text: str
    unsupported_metrics: tuple[str, ...]
    evidence_request: str | None


def enforce_metric_evidence(original: str, proposed: str) -> EvidenceDecision:
    def canonical(metric: str) -> str:
        return re.sub(r"\s+", "", metric).replace(",", "").casefold()

    original_metrics = {canonical(metric) for metric in _METRIC_PATTERN.findall(original)}
    unsupported = tuple(
        metric
        for metric in _METRIC_PATTERN.findall(proposed)
        if canonical(metric) not in original_metrics
    )
    if not unsupported:
        return EvidenceDecision(proposed, (), None)
    request = (
        "Please provide source evidence for "
        + ", ".join(unsupported)
        + "; the metric was omitted from this proposal."
    )
    return EvidenceDecision(original, unsupported, request)
