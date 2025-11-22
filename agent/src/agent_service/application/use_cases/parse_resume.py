"""Parse Resume Use Case"""
from typing import Tuple
from ...domain.models import Resume
from ...infra.parsing.pdf_parser import PDFParser
from ...infra.parsing.docx_parser import DOCXParser
from ...infra.nlp.section_extractor import SectionExtractor
from ...infra.storage.files import FileStorage


class ParseResumeUseCase:
    """Use case for parsing resume files"""

    def __init__(self, section_extractor: SectionExtractor, file_storage: FileStorage):
        """
        Initialize parse resume use case

        Args:
            section_extractor: Section extractor instance
            file_storage: File storage instance
        """
        self.section_extractor = section_extractor
        self.file_storage = file_storage
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()

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
        file_ext = self.file_storage.get_file_extension(filename)

        # Extract text based on file type
        if file_ext == 'pdf':
            text = self.pdf_parser.extract_text(file_content)
        elif file_ext in ['docx', 'doc']:
            text = self.docx_parser.extract_text(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Only PDF and DOCX are supported.")

        # Extract structured data using LLM
        resume = await self.section_extractor.extract_resume_data(text)

        return resume
