"""Small typed registry for capabilities available to the agent workflow."""

from dataclasses import dataclass
from enum import Enum
from typing import Awaitable, Callable, Generic, Iterable, TypeVar

from pydantic import BaseModel


InputT = TypeVar("InputT", bound=BaseModel)
ResultT = TypeVar("ResultT", bound=BaseModel)


class ToolEffect(str, Enum):
    READ = "read"
    PROPOSAL = "proposal"
    MUTATION = "mutation"


class ToolNotAllowedError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolContext:
    """Trusted execution context supplied by the application, never by the model."""

    owner: str | None = None
    run_id: str | None = None


ToolHandler = Callable[[InputT, ToolContext], Awaitable[ResultT]]


@dataclass(frozen=True)
class ToolSpec(Generic[InputT, ResultT]):
    name: str
    input_type: type[InputT]
    result_type: type[ResultT]
    effect: ToolEffect
    allowed_states: frozenset[str]
    handler: ToolHandler[InputT, ResultT]

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_states", frozenset(self.allowed_states))

    def metadata(self) -> dict:
        return {
            "name": self.name,
            "effect": self.effect.value,
            "allowed_states": sorted(self.allowed_states),
            "input_schema": self.input_type.model_json_schema(),
            "result_type": self.result_type.__name__,
        }


class ToolRegistry:
    def __init__(self, tools: Iterable[ToolSpec] = ()):
        self._tools: dict[str, ToolSpec] = {}
        for tool in tools:
            if tool.name in self._tools:
                raise ValueError(f"Duplicate tool: {tool.name}")
            self._tools[tool.name] = tool

    def describe(self, state: str | None = None) -> list[dict]:
        tools = self._tools.values()
        if state is not None:
            tools = (tool for tool in tools if state in tool.allowed_states)
        return [tool.metadata() for tool in tools]

    async def execute(
        self,
        name: str,
        arguments: dict,
        *,
        state: str,
        owner: str | None = None,
        run_id: str | None = None,
        context: ToolContext | None = None,
    ) -> BaseModel:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name}")
        if state not in tool.allowed_states:
            raise ToolNotAllowedError(f"Tool {name} is not allowed in state {state}")

        parsed = tool.input_type.model_validate(arguments)
        trusted_context = context or ToolContext(owner=owner, run_id=run_id)
        result = await tool.handler(parsed, trusted_context)
        if not isinstance(result, tool.result_type):
            raise TypeError(
                f"Tool {name} returned {type(result).__name__}, expected {tool.result_type.__name__}"
            )
        return result
