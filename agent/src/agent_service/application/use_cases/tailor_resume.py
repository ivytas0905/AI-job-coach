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
from ...infra.matching.content_selector import ContentSelector
from ...infra.nlp.bullet_optimizer import BulletOptimizer
from datetime import datetime


class TailorResumeUseCase:
    """Creates a tailored resume from master resume based on JD"""

    def __init__(
        self,
        content_selector: ContentSelector,
        bullet_optimizer: BulletOptimizer
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
        ats_score = self._calculate_ats_score(match_score, all_optimizations)

        # Step 5: Create tailored resume
        tailored = TailoredResume(
            master_resume_id=master_resume.id,
            jd_id=jd.id,
            personal_info=master_resume.personal_info,
            selected_experience_ids=selected_exp_ids,
            selected_bullet_optimizations=all_optimizations,
            selected_education_ids=[edu.id for edu in master_resume.education[:2]],  # Top 2
            selected_skills=self._select_skills(master_resume, jd),
            match_score=match_score,
            ats_score=ats_score,
            created_at=datetime.now()
        )

        return tailored

    def _calculate_ats_score(
        self,
        match_score: float,
        optimizations: List[BulletOptimization]
    ) -> float:
        """
        Calculate ATS score based on match score and optimizations

        Args:
            match_score: Keyword match score
            optimizations: List of bullet optimizations

        Returns:
            ATS score from 0-100
        """
        # Base score from keyword matching (60%)
        ats_score = match_score * 0.6

        # Bonus for having quantifiable metrics (20%)
        if optimizations:
            metrics_count = sum(
                1 for opt in optimizations
                if any('metric' in imp.lower() or 'quantif' in imp.lower() for imp in opt.improvements)
            )
            metrics_ratio = metrics_count / len(optimizations)
            ats_score += metrics_ratio * 20

        # Bonus for keyword-rich bullets (20%)
        if optimizations:
            avg_keywords = sum(len(opt.keyword_matches) for opt in optimizations) / len(optimizations)
            keyword_bonus = min((avg_keywords / 3) * 20, 20)  # Up to 20 points
            ats_score += keyword_bonus

        return min(ats_score, 100.0)

    def _select_skills(
        self,
        master_resume: MasterResume,
        jd: JobDescription
    ) -> List[str]:
        """
        Select most relevant skills

        Args:
            master_resume: Master resume
            jd: Job description

        Returns:
            List of selected skill names
        """
        jd_skills = set([s.lower() for s in jd.required_skills + jd.preferred_skills])
        resume_skills = [skill.name for skill in master_resume.skills if skill.name]

        # Match resume skills with JD skills
        matched_skills = []
        unmatched_skills = []

        for skill_name in resume_skills:
            if skill_name.lower() in jd_skills:
                matched_skills.append(skill_name)
            else:
                unmatched_skills.append(skill_name)

        # Select matched skills first, then fill with unmatched up to 15 total
        selected = matched_skills[:15]
        if len(selected) < 15:
            selected.extend(unmatched_skills[:(15 - len(selected))])

        return selected
