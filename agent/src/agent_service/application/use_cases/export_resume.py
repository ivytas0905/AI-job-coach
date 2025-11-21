from domain.models import Resume
from typing import Literal
from dataclasses import asdict

class ExportResumeUseCase:
    """导出简历的业务逻辑"""
    
    def __init__(self, pdf_generator, word_generator):
        self.pdf_generator = pdf_generator
        self.word_generator = word_generator
    
    def execute(
        self, 
        resume: Resume, 
        format: Literal['pdf', 'word'],
        template: str = "professional"
    ) -> bytes:
        """
        Export resume to specified format
        
        Args:
            resume: Resume domain model
            format: Export format ('pdf' or 'word')
            template: Template name (e.g., 'professional', 'simple', 'modern')
            
        Returns:
            File content as bytes
            
        Raises:
            ValueError: If format is not supported
        """
        if format == 'pdf':
            return self.pdf_generator.generate(resume, template)
        elif format == 'word':
            return self.word_generator.generate(resume, template)
        else:
            raise ValueError(f"Unsupported format: {format}")