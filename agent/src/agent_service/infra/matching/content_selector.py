"""
Content Selector - Selects most relevant content from Master Resume based on JD
"""
from typing import List, Tuple, Dict
from ...domain.models import (
    MasterResume,
    JobDescription,
    Experience,
    BulletPoint,
    KeywordWeight
)


class ContentSelector:
    """Selects relevant experiences and bullets based on JD"""

    def __init__(self):
        pass

    def select_content(
        self,
        master_resume: MasterResume,
        jd: JobDescription,
        max_experiences: int = 4,
        max_bullets_per_exp: int = 4
    ) -> Tuple[List[Experience], Dict[str, List[BulletPoint]]]:
        """
        Select most relevant experiences and bullets

        Args:
            master_resume: Master resume with all experiences
            jd: Analyzed job description
            max_experiences: Maximum number of experiences to select
            max_bullets_per_exp: Maximum bullets per experience

        Returns:
            Tuple of (selected_experiences, dict of experience_id -> selected_bullets)
        """
        # Score all experiences
        exp_scores = []
        for exp in master_resume.experiences:
            score = self._score_experience(exp, jd)
            exp_scores.append((exp, score))

        # Sort by score and select top N
        exp_scores.sort(key=lambda x: x[1], reverse=True)
        selected_exps = [exp for exp, _ in exp_scores[:max_experiences]]

        # For each selected experience, select best bullets
        selected_bullets_map = {}
        for exp in selected_exps:
            bullets = self._select_bullets(exp, jd, max_bullets_per_exp)
            selected_bullets_map[exp.id] = bullets

        return selected_exps, selected_bullets_map

    def _score_experience(self, experience: Experience, jd: JobDescription) -> float:
        """
        Calculate relevance score for an experience

        Scoring breakdown:
        - Skill match: 40%
        - Keyword match in bullets: 30%
        - Industry match: 15%
        - Responsibility relevance: 15%
        """
        score = 0.0

        # 1. Skill matching (40 points)
        if experience.skills_used:
            jd_skills = set([s.lower() for s in jd.required_skills + jd.preferred_skills])
            exp_skills = set([s.lower() for s in experience.skills_used])
            skill_overlap = exp_skills & jd_skills

            if jd_skills:
                skill_match_ratio = len(skill_overlap) / len(jd_skills)
                score += skill_match_ratio * 40

        # 2. Keyword matching in bullets (30 points)
        jd_keywords = [kw.text.lower() for kw in jd.keywords]
        keyword_matches = 0

        for bullet in experience.bullets:
            bullet_text_lower = bullet.text.lower()
            for keyword in jd_keywords:
                if keyword in bullet_text_lower:
                    keyword_matches += 1

        # Normalize keyword matches
        if jd_keywords and experience.bullets:
            max_possible_matches = len(jd_keywords) * len(experience.bullets)
            keyword_score = min((keyword_matches / max_possible_matches) * 100, 30)
            score += keyword_score

        # 3. Industry matching (15 points)
        if experience.industry and jd.industry:
            if experience.industry.lower() == jd.industry.lower():
                score += 15
            elif jd.industry.lower() in experience.industry.lower():
                score += 10

        # 4. Responsibility relevance (15 points)
        # Check if experience bullets match JD responsibilities
        if jd.responsibilities and experience.bullets:
            resp_matches = 0
            for resp in jd.responsibilities:
                resp_lower = resp.lower()
                for bullet in experience.bullets:
                    if any(word in bullet.text.lower() for word in resp_lower.split()[:3]):
                        resp_matches += 1
                        break

            if jd.responsibilities:
                resp_score = (resp_matches / len(jd.responsibilities)) * 15
                score += resp_score

        return score

    def _select_bullets(
        self,
        experience: Experience,
        jd: JobDescription,
        max_bullets: int
    ) -> List[BulletPoint]:
        """
        Select most relevant bullets from an experience

        Args:
            experience: Experience to select bullets from
            jd: Job description
            max_bullets: Maximum number of bullets to select

        Returns:
            List of selected bullet points
        """
        if not experience.bullets:
            return []

        # Score each bullet
        bullet_scores = []
        for bullet in experience.bullets:
            score = self._score_bullet(bullet, jd)
            bullet_scores.append((bullet, score))

        # Sort by score and select top N
        bullet_scores.sort(key=lambda x: x[1], reverse=True)
        selected = [bullet for bullet, _ in bullet_scores[:max_bullets]]

        return selected

    def _score_bullet(self, bullet: BulletPoint, jd: JobDescription) -> float:
        """
        Score a single bullet point

        Scoring:
        - High-weight keyword matches: 50%
        - Medium-weight keyword matches: 30%
        - Has quantifiable metrics: 20%
        """
        score = 0.0
        bullet_text_lower = bullet.text.lower()

        # Check for keyword matches with weighting
        for kw in jd.keywords:
            if kw.text.lower() in bullet_text_lower:
                if kw.weight >= 0.8:  # High priority
                    score += 50 * kw.weight
                elif kw.weight >= 0.6:  # Medium priority
                    score += 30 * kw.weight
                else:  # Low priority
                    score += 10 * kw.weight

        # Bonus for quantifiable metrics (numbers, percentages)
        if self._has_metrics(bullet.text):
            score += 20

        return score

    def _has_metrics(self, text: str) -> bool:
        """
        Check if text contains quantifiable metrics
        """
        import re
        # Look for numbers, percentages, dollar amounts, time periods
        patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+[xX]',  # Multipliers (e.g., 3x)
            r'\d+\+',  # Numbers with plus
            r'\d+[KkMmBb]',  # Thousands/Millions/Billions
            r'\d+\s*(users|customers|requests|transactions)',  # With units
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                return True

        return False

    def calculate_match_score(
        self,
        master_resume: MasterResume,
        jd: JobDescription,
        selected_exp_ids: List[str]
    ) -> float:
        """
        Calculate overall match score between resume and JD

        Args:
            master_resume: Master resume
            jd: Job description
            selected_exp_ids: IDs of selected experiences

        Returns:
            Match score from 0-100
        """
        if not jd.keywords:
            return 50.0  # Default if no keywords

        # Get selected experiences
        selected_exps = [exp for exp in master_resume.experiences if exp.id in selected_exp_ids]

        # Count keyword coverage
        jd_keywords = set([kw.text.lower() for kw in jd.keywords])
        found_keywords = set()

        for exp in selected_exps:
            # Check skills
            for skill in exp.skills_used:
                if skill.lower() in jd_keywords:
                    found_keywords.add(skill.lower())

            # Check bullets
            for bullet in exp.bullets:
                bullet_lower = bullet.text.lower()
                for kw in jd_keywords:
                    if kw in bullet_lower:
                        found_keywords.add(kw)

        # Calculate coverage ratio
        if jd_keywords:
            coverage_ratio = len(found_keywords) / len(jd_keywords)
            match_score = coverage_ratio * 100
        else:
            match_score = 50.0

        return min(match_score, 100.0)
