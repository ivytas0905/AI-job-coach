"""Dependency Injection Container"""
from functools import lru_cache
from .config import get_settings
from .application.ports.llm import LlmProvider
from .infra.llm.registry import build_provider
from .infra.nlp.section_extractor import SectionExtractor
from .infra.nlp.jd_analyzer import JDAnalyzer
from .infra.nlp.bullet_optimizer import BulletOptimizer
from .infra.matching.content_selector import ContentSelector
from .infra.storage.files import FileStorage
from .application.use_cases.parse_resume import ParseResumeUseCase
from .application.use_cases.analyze_jd import AnalyzeJDUseCase
from .application.use_cases.tailor_resume import TailorResumeUseCase

settings = get_settings()


# LLM Provider
@lru_cache()
def get_llm_provider() -> LlmProvider:
    """Build the configured provider only when an LLM capability is requested."""
    return build_provider(settings)


# Section Extractor
@lru_cache()
def get_section_extractor() -> SectionExtractor:
    """Get section extractor instance"""
    llm_provider = get_llm_provider()
    return SectionExtractor(llm_provider)


# JD Analyzer
@lru_cache()
def get_jd_analyzer() -> JDAnalyzer:
    """Get JD analyzer instance"""
    llm_provider = get_llm_provider()
    return JDAnalyzer(llm_provider)


# Bullet Optimizer
@lru_cache()
def get_bullet_optimizer() -> BulletOptimizer:
    """Get bullet optimizer instance"""
    llm_provider = get_llm_provider()
    return BulletOptimizer(llm_provider)


# Content Selector
@lru_cache()
def get_content_selector() -> ContentSelector:
    """Get content selector instance"""
    return ContentSelector()


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


def get_analyze_jd_use_case() -> AnalyzeJDUseCase:
    """Get analyze JD use case instance"""
    jd_analyzer = get_jd_analyzer()
    return AnalyzeJDUseCase(jd_analyzer)


def get_tailor_resume_use_case() -> TailorResumeUseCase:
    """Get tailor resume use case instance"""
    content_selector = get_content_selector()
    bullet_optimizer = get_bullet_optimizer()
    return TailorResumeUseCase(content_selector, bullet_optimizer)


# ========== New Enhanced Services (Phase 2-4) ==========

# Database Manager
from .infra.storage.database import get_db_manager

@lru_cache()
def get_database_manager():
    """Get database manager instance"""
    return get_db_manager(
        database_url=settings.database_url,
        echo=settings.database_echo
    )


# Memory Cache Service
from .infra.cache.memory_cache import get_cache_service

@lru_cache()
def get_memory_cache():
    """Get memory cache service instance"""
    return get_cache_service()


# Vector Store
from .infra.vector.simple_vector_store import get_vector_store

@lru_cache()
def get_simple_vector_store():
    """Get simple vector store instance"""
    return get_vector_store()
