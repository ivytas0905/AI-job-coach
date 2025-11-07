"""
Analyze Job Description Use Case
"""
from ...domain.models import JobDescription
from ...infra.nlp.jd_analyzer import JDAnalyzer
from datetime import datetime


class AnalyzeJDUseCase:
    """Analyzes job description and extracts structured information"""

    def __init__(self, jd_analyzer: JDAnalyzer):
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
        # Validate input
        if not raw_text or len(raw_text.strip()) < 50:
            raise ValueError("Job description must be at least 50 characters")

        # Analyze JD
        jd = await self.jd_analyzer.analyze(raw_text.strip())

        # Set analysis timestamp
        jd.analyzed_at = datetime.now()

        return jd
