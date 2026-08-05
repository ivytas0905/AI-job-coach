import httpx

from agent_service.application.ports.llm import LlmMessage
from agent_service.infra.llm.providers import DeepSeekProvider


async def test_provider_contract_normalizes_text_and_identity():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat/completions"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"content": "ready"}}
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            },
        )

    provider = DeepSeekProvider(
        "secret",
        "deepseek-chat",
        "https://example.test",
        transport=httpx.MockTransport(handler),
    )
    try:
        result = await provider.complete([LlmMessage("user", "hello")])
    finally:
        await provider.close()

    assert provider.provider_name == "deepseek"
    assert provider.model == "deepseek-chat"
    assert result.text == "ready"
    assert result.finish_reason == "stop"
    assert result.tool_requests == ()
    assert result.usage == {"prompt_tokens": 1, "completion_tokens": 1}
