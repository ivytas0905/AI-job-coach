"""External resume capabilities coordinated by application use cases."""

from typing import Protocol

from ...domain.models import BulletOptimization, BulletPoint, Experience, JobDescription, MasterResume


class ContentSelectorPort(Protocol):
    def select_content(self, master_resume: MasterResume, jd: JobDescription, max_experiences: int = 4, max_bullets_per_exp: int = 4) -> tuple[list[Experience], dict[str, list[BulletPoint]]]: ...
    def calculate_match_score(self, master_resume: MasterResume, jd: JobDescription, selected_exp_ids: list[str]) -> float: ...


class BulletOptimizerPort(Protocol):
    async def optimize_multiple_bullets(self, bullets: list[BulletPoint], jd: JobDescription, experience_context: str = "") -> list[BulletOptimization]: ...
