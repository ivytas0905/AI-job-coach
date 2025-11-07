"""
Enhanced JD Analysis Use Case with Caching

This extends the basic JD analysis with:
- LLM-based keyword extraction (TOP 20)
- Redis/Memory caching
- Database persistence
"""

from typing import Dict, Any, Optional
import hashlib
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...infra.llm.enhanced_llm import EnhancedLLMService
from ...infra.cache.memory_cache import MemoryCacheService
from ...infra.storage.models import JDAnalysisModel


class JDAnalysisEnhancedUseCase:
    """
    Enhanced JD Analysis use case.

    Features:
    - TOP 20 keyword extraction using GPT-4
    - Caching to avoid redundant API calls
    - Database persistence for history tracking
    """

    def __init__(
        self,
        llm_service: EnhancedLLMService,
        cache_service: MemoryCacheService,
        db_session: AsyncSession
    ):
        """
        Initialize use case.

        Args:
            llm_service: Enhanced LLM service for analysis
            cache_service: Cache service for storing results
            db_session: Database session for persistence
        """
        self.llm = llm_service
        self.cache = cache_service
        self.db = db_session

    async def execute(
        self,
        jd_text: str,
        job_title: str,
        company: Optional[str] = None,
        job_url: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze job description with caching.

        Args:
            jd_text: Raw job description text
            job_title: Job title
            company: Company name (optional)
            job_url: URL to job posting (optional)
            user_id: User ID for tracking (optional)

        Returns:
            Analysis result dictionary with:
            {
                "jd_id": str,
                "top_keywords": [...],
                "required_skills": [...],
                "preferred_skills": [...],
                "common_verbs": [...],
                "industry": str,
                "cached": bool
            }

        Raises:
            ValueError: If JD text is too short
        """
        # Validate input
        if not jd_text or len(jd_text.strip()) < 50:
            raise ValueError("Job description must be at least 50 characters")

        jd_text = jd_text.strip()

        # Generate hash for caching
        jd_hash = self._generate_hash(jd_text)
        cache_key = f"jd_analysis:{jd_hash}"

        # Try to get from cache
        cached_result = await self.cache.get_json(cache_key)
        if cached_result:
            print(f"✓ JD analysis retrieved from cache (hash: {jd_hash[:8]}...)")
            cached_result["cached"] = True
            return cached_result

        # Check database
        db_result = await self._get_from_database(jd_hash)
        if db_result:
            print(f"✓ JD analysis retrieved from database (hash: {jd_hash[:8]}...)")
            # Cache for future requests
            await self.cache.set_json(cache_key, db_result, ttl=7*24*3600)  # 7 days
            db_result["cached"] = True
            return db_result

        # Analyze using LLM
        print(f"→ Analyzing JD with LLM (hash: {jd_hash[:8]}...)...")
        analysis = await self.llm.analyze_jd(jd_text, job_title)

        # Create JD analysis model for database
        jd_analysis = JDAnalysisModel(
            user_id=user_id or "anonymous",
            company=company,
            job_title=job_title,
            job_url=job_url,
            raw_text=jd_text,
            jd_hash=jd_hash,
            analysis_result=analysis,
            analyzed_at=datetime.utcnow()
        )

        # Save to database
        self.db.add(jd_analysis)
        await self.db.commit()
        await self.db.refresh(jd_analysis)

        # Prepare result
        result = {
            "jd_id": jd_analysis.id,
            "top_keywords": analysis.get("top_keywords", []),
            "required_skills": analysis.get("required_skills", []),
            "preferred_skills": analysis.get("preferred_skills", []),
            "common_verbs": analysis.get("common_verbs", []),
            "common_nouns": analysis.get("common_nouns", []),
            "industry": analysis.get("industry", "unknown"),
            "cached": False
        }

        # Cache the result
        await self.cache.set_json(cache_key, result, ttl=7*24*3600)  # 7 days

        print(f"✓ JD analysis completed and cached (hash: {jd_hash[:8]}...)")

        return result

    async def get_analysis_by_id(self, jd_id: str) -> Optional[Dict[str, Any]]:
        """
        Get JD analysis by ID from database.

        Args:
            jd_id: JD analysis ID

        Returns:
            Analysis result or None if not found
        """
        stmt = select(JDAnalysisModel).where(JDAnalysisModel.id == jd_id)
        result = await self.db.execute(stmt)
        jd_analysis = result.scalar_one_or_none()

        if jd_analysis is None:
            return None

        return {
            "jd_id": jd_analysis.id,
            "company": jd_analysis.company,
            "job_title": jd_analysis.job_title,
            "job_url": jd_analysis.job_url,
            "analyzed_at": jd_analysis.analyzed_at.isoformat(),
            **jd_analysis.analysis_result
        }

    async def get_user_analysis_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Get user's JD analysis history.

        Args:
            user_id: User ID
            limit: Maximum number of results

        Returns:
            List of analysis results
        """
        stmt = (
            select(JDAnalysisModel)
            .where(JDAnalysisModel.user_id == user_id)
            .order_by(JDAnalysisModel.analyzed_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        analyses = result.scalars().all()

        return [
            {
                "jd_id": analysis.id,
                "company": analysis.company,
                "job_title": analysis.job_title,
                "analyzed_at": analysis.analyzed_at.isoformat(),
                "keyword_count": len(analysis.analysis_result.get("top_keywords", []))
            }
            for analysis in analyses
        ]

    async def _get_from_database(self, jd_hash: str) -> Optional[Dict[str, Any]]:
        """
        Try to get analysis from database by hash.

        Args:
            jd_hash: JD text hash

        Returns:
            Analysis result or None if not found
        """
        stmt = select(JDAnalysisModel).where(JDAnalysisModel.jd_hash == jd_hash)
        result = await self.db.execute(stmt)
        jd_analysis = result.scalar_one_or_none()

        if jd_analysis is None:
            return None

        return {
            "jd_id": jd_analysis.id,
            "top_keywords": jd_analysis.analysis_result.get("top_keywords", []),
            "required_skills": jd_analysis.analysis_result.get("required_skills", []),
            "preferred_skills": jd_analysis.analysis_result.get("preferred_skills", []),
            "common_verbs": jd_analysis.analysis_result.get("common_verbs", []),
            "common_nouns": jd_analysis.analysis_result.get("common_nouns", []),
            "industry": jd_analysis.analysis_result.get("industry", "unknown")
        }

    def _generate_hash(self, text: str) -> str:
        """
        Generate hash for JD text for caching.

        Args:
            text: JD text

        Returns:
            MD5 hash string
        """
        return hashlib.md5(text.encode()).hexdigest()
