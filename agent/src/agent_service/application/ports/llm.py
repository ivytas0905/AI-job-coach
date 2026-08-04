"""Provider-neutral LLM contracts used by the application layer."""

from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class LlmMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ToolRequest:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LlmResult:
    text: str | None
    finish_reason: str
    tool_requests: tuple[ToolRequest, ...] = ()
    usage: dict[str, int] = field(default_factory=dict)


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
