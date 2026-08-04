"""
Base generator interface
"""
from abc import ABC, abstractmethod
from ...domain.models import Resume


class ResumeGenerator(ABC):
    """Base class for resume generators"""
    
    @abstractmethod
    def generate(self, resume: Resume, template: str) -> bytes:
        """Generate resume file and return bytes"""
        pass
