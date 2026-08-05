"""Configured LLM provider registry."""

from ...application.ports.llm import LlmProvider
from ...config import Settings
from .providers import DeepSeekProvider, OpenAIProvider, TogetherAIProvider


def build_provider(
    settings: Settings,
    *,
    provider_name: str | None = None,
    model: str | None = None,
) -> LlmProvider:
    """Build either the deployment default or a conversation-pinned provider."""
    selected_provider = provider_name or settings.llm_provider
    provider_configs = {
        "deepseek": (
            DeepSeekProvider,
            settings.deepseek_api_key,
            settings.deepseek_base_url,
            "RESUME_DEEPSEEK_API_KEY",
        ),
        "openai": (
            OpenAIProvider,
            settings.openai_api_key,
            settings.openai_base_url,
            "RESUME_OPENAI_API_KEY",
        ),
        "togetherai": (
            TogetherAIProvider,
            settings.together_api_key,
            settings.together_base_url,
            "RESUME_TOGETHER_API_KEY",
        ),
    }
    if selected_provider not in provider_configs:
        raise ValueError(f"Unsupported LLM provider: {selected_provider}")
    provider_type, api_key, base_url, credential_name = provider_configs[selected_provider]
    if not api_key:
        raise ValueError(f"{credential_name} is required when the LLM provider is used")
    return provider_type(
        api_key=api_key,
        model=model or settings.llm_model,
        base_url=base_url,
        timeout=settings.llm_timeout_seconds,
    )
