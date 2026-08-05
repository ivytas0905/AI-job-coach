import pytest

from agent_service.config import Settings
from agent_service.infra.llm.registry import build_provider


def test_registry_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported"):
        build_provider(Settings(llm_provider="unknown"))


def test_registry_requires_deepseek_credentials():
    with pytest.raises(ValueError, match="RESUME_DEEPSEEK_API_KEY"):
        build_provider(Settings(llm_provider="deepseek", deepseek_api_key=None))


@pytest.mark.parametrize(
    ("provider_name", "api_key_field", "expected_type"),
    [
        ("openai", "openai_api_key", "OpenAIProvider"),
        ("togetherai", "together_api_key", "TogetherAIProvider"),
    ],
)
def test_registry_builds_configured_provider(
    provider_name, api_key_field, expected_type
):
    settings = Settings(
        llm_provider=provider_name,
        llm_model="configured-model",
        **{api_key_field: "secret"},
    )

    provider = build_provider(settings)

    assert type(provider).__name__ == expected_type
    assert provider.provider_name == provider_name
    assert provider.model == "configured-model"


@pytest.mark.parametrize(
    ("provider_name", "setting_name"),
    [("openai", "RESUME_OPENAI_API_KEY"), ("togetherai", "RESUME_TOGETHER_API_KEY")],
)
def test_registry_requires_selected_provider_credentials(provider_name, setting_name):
    with pytest.raises(ValueError, match=setting_name):
        build_provider(Settings(llm_provider=provider_name))


def test_registry_uses_pinned_provider_and_model():
    settings = Settings(
        llm_provider="unknown-default",
        llm_model="new-default",
        deepseek_api_key="secret",
    )

    provider = build_provider(settings, provider_name="deepseek", model="pinned-model")

    assert provider.provider_name == "deepseek"
    assert provider.model == "pinned-model"
