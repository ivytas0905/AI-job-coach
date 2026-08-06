"""
Tailor Resume Use Case - Creates customized resume based on JD
"""
from typing import List
from ...domain.models import (
    MasterResume,
    JobDescription,
    TailoredResume,
    BulletOptimization
)
from ..ports.resume import BulletOptimizerPort, ContentSelectorPort
from ...domain.resume_policies import calculate_ats_score, select_skills
from datetime import datetime


class TailorResumeUseCase:
    """Creates a tailored resume from master resume based on JD"""

    def __init__(
        self,
        content_selector: ContentSelectorPort,
        bullet_optimizer: BulletOptimizerPort
    ):
        self.content_selector = content_selector
        self.bullet_optimizer = bullet_optimizer

    async def execute(
        self,
        master_resume: MasterResume,
        jd: JobDescription
    ) -> TailoredResume:
        """
        Create tailored resume

        Args:
            master_resume: Master resume with all experiences
            jd: Analyzed job description

        Returns:
            TailoredResume with selected and optimized content
        """
        # Step 1: Select most relevant experiences and bullets
        selected_exps, selected_bullets_map = self.content_selector.select_content(
            master_resume,
            jd,
            max_experiences=4,
            max_bullets_per_exp=4
        )

        # Step 2: Optimize selected bullets
        all_optimizations: List[BulletOptimization] = []

        for exp in selected_exps:
            bullets_to_optimize = selected_bullets_map.get(exp.id, [])

            if bullets_to_optimize:
                # Create context string for optimizer
                context = f"{exp.title} at {exp.company}"

                # Optimize bullets for this experience
                optimizations = await self.bullet_optimizer.optimize_multiple_bullets(
                    bullets_to_optimize,
                    jd,
                    context
                )

                all_optimizations.extend(optimizations)

        # Step 3: Calculate match score
        selected_exp_ids = [exp.id for exp in selected_exps]
        match_score = self.content_selector.calculate_match_score(
            master_resume,
            jd,
            selected_exp_ids
        )

        # Step 4: Calculate ATS score (simplified for MVP)
        ats_score = calculate_ats_score(match_score, all_optimizations)

        # Step 5: Create tailored resume
        tailored = TailoredResume(
            master_resume_id=master_resume.id,
            jd_id=jd.id,
            personal_info=master_resume.personal_info,
            selected_experience_ids=selected_exp_ids,
            selected_bullet_optimizations=all_optimizations,
            selected_education_ids=[edu.id for edu in master_resume.education[:2]],  # Top 2
            selected_skills=select_skills(master_resume, jd),
            match_score=match_score,
            ats_score=ats_score,
            created_at=datetime.now()
        )

        return tailored
