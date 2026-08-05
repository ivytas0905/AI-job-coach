"""Domain ports unrelated to external LLM transport capabilities."""

from typing import List, Protocol, TypedDict

from .models import Resume


class ResumeParserPort(Protocol):
    async def parse(self, file_content: bytes, filename: str) -> Resume: ...


class OptimizeResult(TypedDict):
    optimized_resume: Resume
    ats_score: int
    suggestions: List[str]


class ResumeOptimizerPort(Protocol):
    async def optimize(
        self,
        resume: Resume,
        target_position: str,
    ) -> OptimizeResult: ...
