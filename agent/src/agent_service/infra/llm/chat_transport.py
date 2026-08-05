"""Shared chat-completions HTTP transport and response normalization."""

import json
from typing import Any, Sequence

import httpx

from ...application.ports.llm import LlmMessage, LlmResult, ProviderError, ToolRequest


class ChatTransport:
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
            "messages": [self._message_payload(item) for item in messages],
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
            category = (
                "authentication"
                if status in (401, 403)
                else "rate_limit"
                if status == 429
                else "server"
            )
            raise ProviderError(
                category, f"LLM provider returned HTTP {status}"
            ) from exc

        except httpx.HTTPError as exc:
            raise ProviderError("network", "LLM provider request failed") from exc

        try:
            data = response.json()
            choices = data["choices"]
            if not isinstance(choices, list) or not choices:
                raise ValueError("choices must be a non-empty list")
            choice = choices[0]
            message = choice["message"]
            if not isinstance(message, dict):
                raise ValueError("message must be an object")

            requests = []
            for call in message.get("tool_calls") or []:
                arguments = json.loads(call["function"]["arguments"])
                if not isinstance(arguments, dict):
                    raise ValueError("tool arguments must be an object")
                requests.append(
                    ToolRequest(call["id"], call["function"]["name"], arguments)
                )

            usage = data.get("usage") or {}
            if not isinstance(usage, dict):
                raise ValueError("usage must be an object")
            return LlmResult(
                text=message.get("content"),
                finish_reason=choice.get("finish_reason", "unknown"),
                tool_requests=tuple(requests),
                usage={key: int(value) for key, value in usage.items()},
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ProviderError(
                "invalid_response", "LLM provider returned an invalid response"
            ) from exc

    @staticmethod
    def _message_payload(message: LlmMessage) -> dict[str, Any]:
        payload: dict[str, Any] = {"role": message.role, "content": message.content}
        if message.tool_requests:
            payload["tool_calls"] = [
                {"id": request.id, "type": "function", "function": {
                    "name": request.name, "arguments": json.dumps(request.arguments)
                }} for request in message.tool_requests
            ]
        if message.tool_call_id is not None:
            payload["tool_call_id"] = message.tool_call_id
        return payload

    async def close(self) -> None:
        await self._client.aclose()
