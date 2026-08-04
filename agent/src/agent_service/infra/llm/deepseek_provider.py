"""DeepSeek transport adapter."""

import json
from typing import Any, Sequence

import httpx

from ...application.ports.llm import LlmMessage, LlmResult, ToolRequest


class ProviderError(RuntimeError):
    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category


class DeepSeekProvider:
    provider_name = "deepseek"

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
            transport=transport,
        )

    async def complete(
        self,
        messages: Sequence[LlmMessage],
        *,
        tools: Sequence[dict[str, Any]] = (),
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> LlmResult:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": item.role, "content": item.content} for item in messages],
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = list(tools)
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderError("timeout", "LLM provider timed out") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            category = "authentication" if status in (401, 403) else "rate_limit" if status == 429 else "server"
            raise ProviderError(category, f"LLM provider returned HTTP {status}") from exc
        except httpx.HTTPError as exc:
            raise ProviderError("network", "LLM provider request failed") from exc

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]
        requests = []
        for call in message.get("tool_calls") or []:
            try:
                arguments = json.loads(call["function"]["arguments"])
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                raise ProviderError("invalid_response", "Provider returned malformed tool arguments") from exc
            if not isinstance(arguments, dict):
                raise ProviderError("invalid_response", "Tool arguments must be a JSON object")
            requests.append(ToolRequest(call["id"], call["function"]["name"], arguments))
        return LlmResult(
            text=message.get("content"),
            finish_reason=choice.get("finish_reason", "unknown"),
            tool_requests=tuple(requests),
            usage={key: int(value) for key, value in (data.get("usage") or {}).items()},
        )

    async def close(self) -> None:
        await self._client.aclose()
