"""Dependency Injection Container"""
from functools import lru_cache
from pathlib import Path
from .config import get_settings
from .application.ports.llm import LlmProvider
from .application.ports.object_storage import ObjectStorage
from .application.ports.retrieval import EvidenceRetriever
from .application.services.export_storage import ExportStorageService
from .infra.llm.registry import build_provider
from .infra.nlp.section_extractor import SectionExtractor
from .infra.parsing.pdf_parser import PDFParser
from .infra.parsing.docx_parser import DOCXParser
from .infra.nlp.jd_analyzer import JDAnalyzer
from .infra.nlp.bullet_optimizer import BulletOptimizer
from .infra.matching.content_selector import ContentSelector
from .infra.storage.files import FileStorage
from .infra.storage.object_store import LocalObjectStorage, S3ObjectStorage
from .infra.storage.workflow_repository import WorkflowRepository
from .application.use_cases.parse_resume import ParseResumeUseCase
from .application.use_cases.analyze_jd import AnalyzeJDUseCase
from .application.use_cases.tailor_resume import TailorResumeUseCase
from .application.use_cases.export_resume import ExportResumeUseCase
from .application.use_cases.build_resume import BuildResumeUseCase
from .application.use_cases.enhance_content import EnhanceContentUseCase, ResumeContentEnhancer
from .agent.orchestrator import TailoringOrchestrator
from .infra.generators.pdf_generator import PDFGenerator
from .infra.generators.word_generator import WordGenerator
from .tools import build_resume_tool_registry
from .infra.vector.evidence_retriever import LocalEvidenceRetriever
from .infra.vector.postgres_evidence_retriever import PostgresEvidenceRetriever

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


@lru_cache()
def get_object_storage() -> ObjectStorage:
    """Build the configured durable object storage adapter."""
    if settings.object_storage_backend == "local":
        return LocalObjectStorage(
            settings.object_storage_root,
            max_size_bytes=settings.max_file_size,
        )
    if settings.object_storage_backend == "s3":
        if not settings.object_storage_bucket:
            raise RuntimeError("RESUME_OBJECT_STORAGE_BUCKET is required for S3 storage")
        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=settings.object_storage_endpoint_url,
            region_name=settings.object_storage_region,
            aws_access_key_id=settings.object_storage_access_key_id,
            aws_secret_access_key=settings.object_storage_secret_access_key,
        )
        return S3ObjectStorage(
            client,
            settings.object_storage_bucket,
            max_size_bytes=settings.max_file_size,
        )
    raise RuntimeError(
        f"Unknown object storage backend: {settings.object_storage_backend}"
    )


# Use Cases
def get_parse_resume_use_case() -> ParseResumeUseCase:
    """Get parse resume use case instance"""
    section_extractor = get_section_extractor()
    return ParseResumeUseCase(section_extractor, PDFParser(), DOCXParser())


def get_analyze_jd_use_case() -> AnalyzeJDUseCase:
    """Get analyze JD use case instance"""
    jd_analyzer = get_jd_analyzer()
    return AnalyzeJDUseCase(jd_analyzer)


def get_tailor_resume_use_case() -> TailorResumeUseCase:
    """Get tailor resume use case instance"""
    content_selector = get_content_selector()
    bullet_optimizer = get_bullet_optimizer()
    return TailorResumeUseCase(content_selector, bullet_optimizer)


def get_build_resume_use_case() -> BuildResumeUseCase:
    return BuildResumeUseCase(ResumeContentEnhancer(get_enhance_content_use_case()))


def get_enhance_content_use_case() -> EnhanceContentUseCase:
    return EnhanceContentUseCase(get_llm_provider())


def get_export_resume_use_case() -> ExportResumeUseCase:
    return ExportResumeUseCase(PDFGenerator(), WordGenerator())


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


@lru_cache()
def get_workflow_repository() -> WorkflowRepository:
    return WorkflowRepository(get_database_manager().async_session_factory)


@lru_cache()
def get_tailoring_orchestrator() -> TailoringOrchestrator:
    evidence_retriever = get_evidence_retriever()
    tools = build_resume_tool_registry(
        parse_resume=get_parse_resume_use_case(),
        analyze_jd=get_analyze_jd_use_case(),
        tailor_resume=get_tailor_resume_use_case(),
        export_resume=get_export_resume_use_case(),
        evidence_retriever=evidence_retriever,
    )
    return TailoringOrchestrator(
        get_workflow_repository(),
        provider=settings.llm_provider,
        model=settings.llm_model,
        llm=get_llm_provider(),
        tools=tools,
        evidence_retriever=evidence_retriever,
    )


@lru_cache()
def get_export_storage_service() -> ExportStorageService:
    return ExportStorageService(get_object_storage(), get_workflow_repository())


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


@lru_cache()
def get_evidence_retriever() -> EvidenceRetriever:
    knowledge_dir = Path(__file__).resolve().parents[2] / "knowledge_base"
    if settings.vector_backend == "local":
        return LocalEvidenceRetriever(get_simple_vector_store(), knowledge_dir)
    if settings.vector_backend == "postgres":
        return PostgresEvidenceRetriever(
            get_database_manager().async_session_factory, knowledge_dir
        )
    raise RuntimeError(f"Unknown vector backend: {settings.vector_backend}")
