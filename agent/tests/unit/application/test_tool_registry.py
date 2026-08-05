import pytest
from pydantic import BaseModel

from agent_service.tool_registry import (
    ToolContext,
    ToolEffect,
    ToolNotAllowedError,
    ToolRegistry,
    ToolSpec,
)


class EchoInput(BaseModel):
    value: str


class EchoResult(BaseModel):
    value: str


async def echo(arguments: EchoInput, context: ToolContext) -> EchoResult:
    return EchoResult(value=arguments.value)


def test_registry_exposes_typed_schema_effect_states_and_result_type():
    registry = ToolRegistry(
        [ToolSpec("read_resume", EchoInput, EchoResult, ToolEffect.READ, {"ready"}, echo)]
    )

    metadata = registry.describe()[0]

    assert metadata["name"] == "read_resume"
    assert metadata["effect"] == "read"
    assert metadata["allowed_states"] == ["ready"]
    assert metadata["input_schema"]["required"] == ["value"]
    assert metadata["result_type"] == "EchoResult"


async def test_registry_validates_arguments_and_returns_declared_type():
    registry = ToolRegistry(
        [ToolSpec("read_resume", EchoInput, EchoResult, ToolEffect.READ, {"ready"}, echo)]
    )

    result = await registry.execute(
        "read_resume", {"value": "ok"}, state="ready", context=ToolContext(owner="user-a")
    )

    assert result == EchoResult(value="ok")


async def test_registry_blocks_tool_outside_allowed_state():
    registry = ToolRegistry(
        [ToolSpec("read_resume", EchoInput, EchoResult, ToolEffect.READ, {"ready"}, echo)]
    )

    with pytest.raises(ToolNotAllowedError, match="not allowed"):
        await registry.execute(
            "read_resume", {"value": "no"}, state="awaiting_resume",
            context=ToolContext(owner="user-a"),
        )


def test_registry_rejects_duplicate_tool_names():
    spec = ToolSpec("read_resume", EchoInput, EchoResult, ToolEffect.READ, {"ready"}, echo)

    with pytest.raises(ValueError, match="Duplicate tool"):
        ToolRegistry([spec, spec])


def test_tool_spec_states_cannot_be_mutated_after_registration():
    spec = ToolSpec("read_resume", EchoInput, EchoResult, ToolEffect.READ, {"ready"}, echo)
    ToolRegistry([spec])

    with pytest.raises(AttributeError):
        spec.allowed_states.add("approved")
