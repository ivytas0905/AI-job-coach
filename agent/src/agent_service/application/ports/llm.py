"""Provider-neutral LLM contracts used by the application layer."""

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, Sequence


ProviderErrorCategory = Literal[
    "authentication",
    "rate_limit",
    "server",
    "timeout",
    "network",
    "invalid_response",
]


class ProviderError(RuntimeError):
    """Provider-neutral failure safe to handle outside transport adapters."""

    def __init__(self, category: ProviderErrorCategory, message: str):
        super().__init__(message)
        self.category = category


@dataclass(frozen=True)
class ToolRequest:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LlmMessage:
    role: str
    content: str | None
    tool_requests: tuple[ToolRequest, ...] = ()
    tool_call_id: str | None = None


@dataclass(frozen=True)
class LlmResult:
    text: str | None
    finish_reason: str
    tool_requests: tuple[ToolRequest, ...] = ()
    usage: dict[str, int] = field(default_factory=dict)


def require_text(result: LlmResult) -> str:
    """Return text for text-only capabilities or reject a tool-only response."""
    if result.text is None:
        raise ProviderError("invalid_response", "LLM provider returned no text")
    return result.text


class LlmProvider(Protocol):
    provider_name: str
    model: str

    async def complete(
        self,
        messages: Sequence[LlmMessage],
        *,
        tools: Sequence[dict[str, Any]] = (),
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> LlmResult: ...
