"""Dependency Injection Container"""
from functools import lru_cache
from .config import get_settings
from .infra.llm.openai_provider import OpenAIProvider
from .infra.nlp.section_extractor import SectionExtractor
from .infra.storage.files import FileStorage
from .application.use_cases.parse_resume import ParseResumeUseCase

settings = get_settings()


# LLM Provider
@lru_cache()
def get_llm_provider() -> OpenAIProvider:
    """Get OpenAI LLM provider instance"""
    return OpenAIProvider(
        api_key=settings.openai_api_key,
        model="gpt-4o-mini"
    )


# Section Extractor
@lru_cache()
def get_section_extractor() -> SectionExtractor:
    """Get section extractor instance"""
    llm_provider = get_llm_provider()
    return SectionExtractor(llm_provider)


# File Storage
@lru_cache()
def get_file_storage() -> FileStorage:
    """Get file storage instance"""
    return FileStorage(upload_dir="uploads")


# Use Cases
def get_parse_resume_use_case() -> ParseResumeUseCase:
    """Get parse resume use case instance"""
    section_extractor = get_section_extractor()
    file_storage = get_file_storage()
    return ParseResumeUseCase(section_extractor, file_storage)
