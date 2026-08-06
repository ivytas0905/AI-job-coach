"""
Analyze Job Description Use Case
"""
import re

from ...domain.models import JobDescription
from ..ports.parsing import JobDescriptionAnalyzer
from datetime import datetime


class AnalyzeJDUseCase:
    """Analyzes job description and extracts structured information"""

    def __init__(self, jd_analyzer: JobDescriptionAnalyzer):
        self.jd_analyzer = jd_analyzer

    async def execute(self, raw_text: str) -> JobDescription:
        """
        Analyze job description

        Args:
            raw_text: Raw job description text

        Returns:
            Analyzed JobDescription

        Raises:
            ValueError: If text is too short or invalid
        """
        normalized_text = re.sub(r"\s+", " ", raw_text or "").strip()
        if len(normalized_text) < 50:
            raise ValueError("Job description must be at least 50 characters")

        # Analyze JD
        jd = await self.jd_analyzer.analyze(normalized_text)

        # Set analysis timestamp
        jd.analyzed_at = datetime.now()

        return jd
