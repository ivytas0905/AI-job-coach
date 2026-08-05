import httpx
import pytest

from agent_service.application.ports.llm import LlmMessage, ProviderError, ToolRequest
from agent_service.infra.llm.providers import DeepSeekProvider


async def test_normalizes_text_tools_and_usage():
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
    try:
        result = await provider.complete([LlmMessage("user", "analyze")])
    finally:
        await provider.close()

    assert result.finish_reason == "tool_calls"
    assert result.tool_requests[0].name == "analyze_jd"
    assert result.tool_requests[0].arguments == {"jd_id": "jd-1"}
    assert result.usage["total_tokens"] == 5


async def test_serializes_assistant_tool_calls_and_correlated_results():
    async def handler(request: httpx.Request) -> httpx.Response:
        messages = __import__("json").loads(request.content)["messages"]
        assert messages[0]["tool_calls"][0]["id"] == "call-1"
        assert messages[1]["tool_call_id"] == "call-1"
        return httpx.Response(200, json={
            "choices": [{"finish_reason": "stop", "message": {"content": "done"}}]
        })

    provider = DeepSeekProvider("secret", "deepseek-chat", "https://example.test",
                                transport=httpx.MockTransport(handler))
    try:
        result = await provider.complete([
            LlmMessage("assistant", None, (ToolRequest("call-1", "echo", {"value": "ok"}),)),
            LlmMessage("tool", '{"value":"ok"}', tool_call_id="call-1"),
        ])
    finally:
        await provider.close()
    assert result.text == "done"


async def test_rejects_malformed_tool_arguments():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "choices": [{"finish_reason": "tool_calls", "message": {
                "tool_calls": [{"id": "x", "function": {"name": "tool", "arguments": "not-json"}}]
            }}]
        })

    provider = DeepSeekProvider("secret", "deepseek-chat", "https://example.test", transport=httpx.MockTransport(handler))
    with pytest.raises(ProviderError, match="invalid response") as error:
        try:
            await provider.complete([LlmMessage("user", "go")])
        finally:
            await provider.close()
    assert error.value.category == "invalid_response"


@pytest.mark.parametrize(
    ("status", "category"),
    [(401, "authentication"), (403, "authentication"), (429, "rate_limit"), (500, "server")],
)
async def test_normalizes_http_errors(status, category):
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "provider detail must stay private"})

    provider = DeepSeekProvider(
        "secret",
        "deepseek-chat",
        "https://example.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderError) as error:
        try:
            await provider.complete([LlmMessage("user", "go")])
        finally:
            await provider.close()
    assert error.value.category == category
    assert "provider detail" not in str(error.value)


async def test_normalizes_malformed_response():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    provider = DeepSeekProvider(
        "secret",
        "deepseek-chat",
        "https://example.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderError) as error:
        try:
            await provider.complete([LlmMessage("user", "go")])
        finally:
            await provider.close()
    assert error.value.category == "invalid_response"


@pytest.mark.parametrize(
    ("exception_factory", "category"),
    [
        (lambda request: httpx.ReadTimeout("slow", request=request), "timeout"),
        (lambda request: httpx.ConnectError("offline", request=request), "network"),
    ],
)
async def test_normalizes_transport_errors(exception_factory, category):
    async def handler(request: httpx.Request) -> httpx.Response:
        raise exception_factory(request)

    provider = DeepSeekProvider(
        "secret",
        "deepseek-chat",
        "https://example.test",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderError) as error:
        try:
            await provider.complete([LlmMessage("user", "go")])
        finally:
            await provider.close()
    assert error.value.category == category
