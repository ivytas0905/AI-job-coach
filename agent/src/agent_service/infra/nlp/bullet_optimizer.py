"""
Bullet Point Optimizer - Rewrites bullets using STAR framework and JD keywords
"""
from typing import List
from ...domain.models import BulletPoint, JobDescription, BulletOptimization
from ...domain.ports import LlmProviderPort


class BulletOptimizer:
    """Optimizes bullet points based on JD requirements"""

    def __init__(self, llm_provider: LlmProviderPort):
        self.llm = llm_provider

    async def optimize_bullet(
        self,
        bullet: BulletPoint,
        jd: JobDescription,
        experience_context: str = ""
    ) -> BulletOptimization:
        """
        Optimize a single bullet point

        Args:
            bullet: Original bullet point
            jd: Job description to optimize for
            experience_context: Context about the experience (company, role)

        Returns:
            BulletOptimization with original and optimized text
        """
        # Get top keywords from JD
        top_keywords = [kw.text for kw in jd.keywords[:15] if kw.weight >= 0.6]

        # Create optimization prompt
        optimized_text = await self._generate_optimized_text(
            bullet.text,
            top_keywords,
            experience_context
        )

        # Identify improvements
        improvements = self._identify_improvements(bullet.text, optimized_text, top_keywords)

        # Find keyword matches
        keyword_matches = [kw for kw in top_keywords if kw.lower() in optimized_text.lower()]

        return BulletOptimization(
            bullet_id=bullet.id,
            original_text=bullet.text,
            optimized_text=optimized_text,
            improvements=improvements,
            keyword_matches=keyword_matches,
            status="pending"
        )

    async def _generate_optimized_text(
        self,
        original_text: str,
        keywords: List[str],
        context: str = ""
    ) -> str:
        """
        Generate optimized bullet text using LLM
        """
        system_prompt = """You are a professional resume writer specializing in ATS-optimized resumes.
Your task is to rewrite bullet points to be more impactful and keyword-rich."""

        context_str = f"\n\nContext: {context}" if context else ""

        prompt = f"""Rewrite this resume bullet point to make it more impactful and ATS-friendly.

Original bullet:
{original_text}
{context_str}

Target keywords to naturally incorporate (if relevant):
{', '.join(keywords[:10])}

Requirements:
1. Use STAR framework when possible (Situation, Task, Action, Result)
2. Include quantifiable metrics if not already present (estimate if needed)
3. Start with a strong action verb
4. Naturally incorporate 2-3 relevant keywords from the list
5. Keep it concise: 1-2 lines maximum (under 95 characters per line)
6. Make the impact clear and specific
7. DO NOT fabricate information - only enhance what's already there

Return ONLY the optimized bullet point, no explanations."""

        try:
            optimized = await self.llm.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=200
            )

            # Clean up the response
            optimized = optimized.strip()
            # Remove leading bullet points or dashes if added
            optimized = optimized.lstrip('•-*').strip()

            return optimized

        except Exception as e:
            print(f"Error optimizing bullet: {e}")
            return original_text

    def _identify_improvements(
        self,
        original: str,
        optimized: str,
        keywords: List[str]
    ) -> List[str]:
        """
        Identify what improvements were made
        """
        improvements = []

        # Check for quantifiable metrics
        import re
        has_numbers_original = bool(re.search(r'\d+', original))
        has_numbers_optimized = bool(re.search(r'\d+', optimized))

        if not has_numbers_original and has_numbers_optimized:
            improvements.append("Added quantifiable metrics")

        # Check for keyword additions
        original_lower = original.lower()
        optimized_lower = optimized.lower()

        new_keywords = []
        for kw in keywords:
            if kw.lower() not in original_lower and kw.lower() in optimized_lower:
                new_keywords.append(kw)

        if new_keywords:
            improvements.append(f"Added keywords: {', '.join(new_keywords[:3])}")

        # Check for stronger action verbs
        strong_verbs = [
            'spearheaded', 'architected', 'engineered', 'orchestrated',
            'pioneered', 'transformed', 'optimized', 'accelerated',
            'championed', 'streamlined', 'revolutionized'
        ]

        has_strong_verb = any(verb in optimized_lower for verb in strong_verbs)
        if has_strong_verb:
            improvements.append("Used stronger action verb")

        # Check for length improvement
        if len(optimized) > len(original) * 1.2:
            improvements.append("Added more specific details")

        # Default if no specific improvements identified
        if not improvements:
            improvements.append("Enhanced clarity and impact")

        return improvements

    async def optimize_multiple_bullets(
        self,
        bullets: List[BulletPoint],
        jd: JobDescription,
        experience_context: str = ""
    ) -> List[BulletOptimization]:
        """
        Optimize multiple bullets

        Args:
            bullets: List of bullet points to optimize
            jd: Job description
            experience_context: Context about the experience

        Returns:
            List of bullet optimizations
        """
        optimizations = []

        for bullet in bullets:
            optimization = await self.optimize_bullet(bullet, jd, experience_context)
            optimizations.append(optimization)

        return optimizations
