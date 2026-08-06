"""Parsing and structured-analysis capabilities."""

from typing import Protocol

from ...domain.models import JobDescription, Resume


class TextParser(Protocol):
    def extract_text(self, file_content: bytes) -> str: ...


class ResumeSectionExtractor(Protocol):
    async def extract_resume_data(self, text: str) -> Resume: ...


class JobDescriptionAnalyzer(Protocol):
    async def analyze(self, raw_text: str) -> JobDescription: ...
