"""Configured LLM provider registry."""

from ...application.ports.llm import LlmProvider
from ...config import Settings
from .deepseek_provider import DeepSeekProvider


def build_provider(settings: Settings) -> LlmProvider:
    if settings.llm_provider != "deepseek":
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    if not settings.deepseek_api_key:
        raise ValueError("RESUME_DEEPSEEK_API_KEY is required when the LLM provider is used")
    return DeepSeekProvider(
        api_key=settings.deepseek_api_key,
        model=settings.llm_model,
        base_url=settings.deepseek_base_url,
        timeout=settings.llm_timeout_seconds,
    )
