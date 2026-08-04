import asyncio
import httpx
import pytest

from agent_service.application.ports.llm import LlmMessage
from agent_service.infra.llm.deepseek_provider import DeepSeekProvider, ProviderError


def test_normalizes_text_tools_and_usage():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer secret"
        return httpx.Response(200, json={
            "choices": [{
                "finish_reason": "tool_calls",
                "message": {
                    "content": None,
                    "tool_calls": [{
                        "id": "call-1",
                        "function": {"name": "analyze_jd", "arguments": '{"jd_id":"jd-1"}'},
                    }],
                },
            }],
            "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
        })

    provider = DeepSeekProvider("secret", "deepseek-chat", "https://example.test", transport=httpx.MockTransport(handler))
    async def exercise():
        result = await provider.complete([LlmMessage("user", "analyze")])
        await provider.close()
        return result

    result = asyncio.run(exercise())

    assert result.finish_reason == "tool_calls"
    assert result.tool_requests[0].name == "analyze_jd"
    assert result.tool_requests[0].arguments == {"jd_id": "jd-1"}
    assert result.usage["total_tokens"] == 5


def test_rejects_malformed_tool_arguments():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "choices": [{"finish_reason": "tool_calls", "message": {
                "tool_calls": [{"id": "x", "function": {"name": "tool", "arguments": "not-json"}}]
            }}]
        })

    provider = DeepSeekProvider("secret", "deepseek-chat", "https://example.test", transport=httpx.MockTransport(handler))
    async def exercise():
        try:
            return await provider.complete([LlmMessage("user", "go")])
        finally:
            await provider.close()

    with pytest.raises(ProviderError, match="malformed") as error:
        asyncio.run(exercise())
    assert error.value.category == "invalid_response"
