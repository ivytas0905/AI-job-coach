import pytest

from agent_service.config import Settings
from agent_service.infra.llm.registry import build_provider


def test_registry_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported"):
        build_provider(Settings(llm_provider="unknown"))


def test_registry_requires_deepseek_credentials():
    with pytest.raises(ValueError, match="RESUME_DEEPSEEK_API_KEY"):
        build_provider(Settings(llm_provider="deepseek", deepseek_api_key=None))
