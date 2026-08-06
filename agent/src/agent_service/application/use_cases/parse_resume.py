"""Parse Resume Use Case"""
import re
from pathlib import Path
from ...domain.models import Resume
from ..ports.parsing import ResumeSectionExtractor, TextParser


class ParseResumeUseCase:
    """Use case for parsing resume files"""

    def __init__(
        self,
        section_extractor: ResumeSectionExtractor,
        pdf_parser: TextParser,
        docx_parser: TextParser,
    ):
        """
        Initialize parse resume use case

        Args:
            section_extractor: Converts normalized text into a resume.
            pdf_parser: Extracts text from PDF bytes.
            docx_parser: Extracts text from Word bytes.
        """
        self.section_extractor = section_extractor
        self.pdf_parser = pdf_parser
        self.docx_parser = docx_parser

    async def execute(self, file_content: bytes, filename: str) -> Resume:
        """
        Parse resume file and extract structured data

        Args:
            file_content: File content bytes
            filename: Original filename

        Returns:
            Parsed Resume object

        Raises:
            ValueError: If file format is not supported
        """
        # Get file extension
        file_ext = Path(filename).suffix.lower().lstrip(".")

        # Extract text based on file type
        if file_ext == 'pdf':
            text = self.pdf_parser.extract_text(file_content)
        elif file_ext in ['docx', 'doc']:
            text = self.docx_parser.extract_text(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Only PDF and DOCX are supported.")

        text = self._normalize_text(text)
        if not text:
            raise ValueError("Resume contains no readable text")

        # Extract structured data using LLM
        resume = await self.section_extractor.extract_resume_data(text)

        # Keep the normalized source available as evidence for later proposals.
        resume.raw_text = text

        return resume

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = []
        for line in text.splitlines():
            normalized = re.sub(r"\s+", " ", line).strip()
            if normalized:
                lines.append(normalized)
        return "\n".join(lines)
