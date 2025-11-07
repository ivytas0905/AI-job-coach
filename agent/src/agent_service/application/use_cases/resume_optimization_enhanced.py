"""
Enhanced Resume Optimization Use Case

Optimizes resume bullet points using STAR framework and target keywords.
"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import re

from ...infra.llm.enhanced_llm import EnhancedLLMService
from ...infra.storage.models import OptimizationHistoryModel
from ...infra.knowledge import get_knowledge_base
from datetime import datetime


class ResumeOptimizationEnhancedUseCase:
    """
    Enhanced resume optimization use case.

    Features:
    - STAR framework application
    - Keyword optimization
    - Quantification suggestions
    - Optimization history tracking
    """

    def __init__(
        self,
        llm_service: EnhancedLLMService,
        db_session: AsyncSession
    ):
        self.llm = llm_service
        self.db = db_session

    async def optimize_resume(
        self,
        resume_data: Dict[str, Any],
        target_keywords: List[str],
        job_title: str,
        resume_version_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Optimize entire resume.

        Args:
            resume_data: Resume data (parsed structure)
            target_keywords: Target keywords from JD analysis
            job_title: Target job title
            resume_version_id: Resume version ID for tracking

        Returns:
            List of optimization suggestions
        """
        optimizations = []
        used_verbs = []  # Track used verbs to ensure variety

        # Optimize experience section
        experiences = resume_data.get('experience', [])
        for exp_idx, exp in enumerate(experiences):
            exp_opts = await self._optimize_experience(
                experience=exp,
                target_keywords=target_keywords,
                job_title=job_title,
                exp_index=exp_idx,
                used_verbs=used_verbs
            )
            optimizations.extend(exp_opts)

        # Save to database if resume_version_id provided
        if resume_version_id:
            await self._save_optimizations(optimizations, resume_version_id)

        return optimizations

    async def _optimize_experience(
        self,
        experience: Dict[str, Any],
        target_keywords: List[str],
        job_title: str,
        exp_index: int,
        used_verbs: List[str]
    ) -> List[Dict[str, Any]]:
        """Optimize bullet points in an experience entry."""
        optimizations = []

        bullet_points = experience.get('bullet_points', [])
        if not bullet_points and experience.get('description'):
            # Convert description to bullet points by splitting on newlines
            description = experience['description']
            bullet_points = [b.strip() for b in description.split('\n') if b.strip()]

        for bullet_idx, bullet in enumerate(bullet_points):
            # Check if optimization needed
            needs_optimization = (
                not self._has_star_structure(bullet) or
                not self._has_quantification(bullet) or
                self._has_missing_keywords(bullet, target_keywords)
            )

            if needs_optimization:
                # Optimize bullet with verb tracking
                optimized = await self.llm.optimize_bullet_star(
                    bullet=bullet,
                    target_keywords=target_keywords[:5],  # Top 5 keywords
                    context={
                        'company': experience.get('company', ''),
                        'title': experience.get('title', ''),
                        'job_title': job_title
                    },
                    used_verbs=used_verbs
                )

                # Extract verb from optimized text (first word)
                first_word = optimized.split()[0] if optimized else ''
                if first_word and first_word[0].isupper():
                    used_verbs.append(first_word)

                # Extract added keywords
                added_keywords = [
                    kw for kw in target_keywords[:5]
                    if kw.lower() not in bullet.lower() and kw.lower() in optimized.lower()
                ]

                # Create subsection identifier
                company = experience.get('company', 'Unknown Company')
                title = experience.get('title', 'Unknown Title')
                subsection = f"{company} - {title}"

                # Generate hints using knowledge base
                kb = get_knowledge_base()
                hints = kb.analyze_bullet_for_hints(bullet)

                optimizations.append({
                    'section': 'experience',
                    'subsection': subsection,
                    'original_text': bullet,
                    'optimized_text': optimized,
                    'improvements': self._get_improvements(bullet, optimized, target_keywords),
                    'score_improvement': self._calculate_score_improvement(bullet, optimized),
                    'keywords_added': added_keywords,
                    'hints': [
                        {
                            'type': hint.type,
                            'message': hint.message,
                            'follow_up_question': hint.follow_up_question,
                            'placeholder': hint.placeholder
                        }
                        for hint in hints
                    ]
                })

        return optimizations

    def _has_star_structure(self, bullet: str) -> bool:
        """Check if bullet has STAR structure."""
        # Check for action verbs
        action_verbs = [
            'developed', 'implemented', 'designed', 'built', 'led',
            'managed', 'improved', 'optimized', 'created', 'architected'
        ]
        has_action = any(verb in bullet.lower() for verb in action_verbs)

        # Check for result indicators
        has_result = any(indicator in bullet for indicator in ['%', 'increased', 'reduced', 'improved'])

        return has_action and has_result

    def _has_quantification(self, bullet: str) -> bool:
        """Check if bullet has quantifiable metrics."""
        patterns = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+[KkMm]',  # K, M notation
            r'\d+\s*(users|customers|clients)',  # User counts
            r'\d+\s*(hours|days|months)'  # Time savings
        ]
        return any(re.search(pattern, bullet) for pattern in patterns)

    def _has_missing_keywords(self, bullet: str, keywords: List[str]) -> bool:
        """Check if bullet is missing important keywords."""
        bullet_lower = bullet.lower()
        # Check top 3 keywords
        missing = [kw for kw in keywords[:3] if kw.lower() not in bullet_lower]
        return len(missing) > 0

    def _get_improvements(
        self,
        original: str,
        optimized: str,
        keywords: List[str]
    ) -> List[str]:
        """Generate list of improvements made."""
        improvements = []

        if not self._has_star_structure(original) and self._has_star_structure(optimized):
            improvements.append('Applied STAR framework')

        if not self._has_quantification(original) and self._has_quantification(optimized):
            improvements.append('Added quantification')

        # Check for added keywords
        added_keywords = [
            kw for kw in keywords[:5]
            if kw.lower() not in original.lower() and kw.lower() in optimized.lower()
        ]
        if added_keywords:
            improvements.append(f"Added keywords: {', '.join(added_keywords)}")

        return improvements

    def _calculate_score_improvement(self, original: str, optimized: str) -> float:
        """Calculate estimated score improvement."""
        original_score = 0
        optimized_score = 0

        # STAR structure (+30 points)
        if self._has_star_structure(original):
            original_score += 30
        if self._has_star_structure(optimized):
            optimized_score += 30

        # Quantification (+20 points)
        if self._has_quantification(original):
            original_score += 20
        if self._has_quantification(optimized):
            optimized_score += 20

        # Length bonus (optimal 10-20 words, +10 points)
        orig_words = len(original.split())
        opt_words = len(optimized.split())
        if 10 <= orig_words <= 20:
            original_score += 10
        if 10 <= opt_words <= 20:
            optimized_score += 10

        return optimized_score - original_score

    async def _save_optimizations(
        self,
        optimizations: List[Dict[str, Any]],
        resume_version_id: str
    ):
        """Save optimizations to database."""
        for idx, opt in enumerate(optimizations):
            history = OptimizationHistoryModel(
                resume_version_id=resume_version_id,
                section=opt['section'],
                item_index=idx,
                original_text=opt['original_text'],
                optimized_text=opt['optimized_text'],
                optimization_type='star_keyword',
                improvements=opt['improvements'],
                target_keywords=opt.get('keywords_added', []),
                user_action=None,  # To be updated when user takes action
                suggested_at=datetime.utcnow()
            )
            self.db.add(history)

        await self.db.commit()
