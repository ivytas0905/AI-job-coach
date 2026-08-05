import pytest
from pydantic import BaseModel

from agent_service.agent.orchestrator import TailoringOrchestrator
from agent_service.application.ports.llm import LlmResult, ToolRequest
from agent_service.agent.state_machine import InvalidTransitionError
from agent_service.tool_registry import ToolContext, ToolEffect, ToolRegistry, ToolSpec


class Run:
    id = "run-1"
    state = "awaiting_resume"
    provider = "deepseek"
    model = "deepseek-chat"


class Repository:
    def __init__(self):
        self.run = Run()

    async def create_run(self, owner, **values):
        assert values["provider"] == "deepseek"
        assert values["model"] == "deepseek-chat"
        return self.run

    async def transition_run(self, owner, run_id, *, expected_state, new_state):
        assert self.run.state == expected_state
        self.run.state = new_state
        return self.run

    async def load_run(self, owner, run_id):
        assert owner == "user-a"
        assert run_id == "run-1"
        return self.run


async def test_new_runs_pin_configured_provider_and_advance_legally():
    service = TailoringOrchestrator(Repository(), provider="deepseek", model="deepseek-chat")
    run = await service.create_run("user-a")

    advanced = await service.record_event("user-a", run.id, "resume_accepted", run.state)

    assert advanced.state == "awaiting_jd"


async def test_orchestrator_rejects_illegal_event_before_persistence():
    repository = Repository()
    service = TailoringOrchestrator(repository, provider="deepseek", model="deepseek-chat")

    with pytest.raises(InvalidTransitionError):
        await service.record_event("user-a", "run-1", "export_requested", "awaiting_resume")


class EvidenceRetriever:
    def __init__(self):
        self.indexed = []

    async def index(self, **values):
        self.indexed.append(values)


async def test_user_evidence_is_recorded_only_through_trusted_orchestrator_command():
    retriever = EvidenceRetriever()
    service = TailoringOrchestrator(
        Repository(), provider="deepseek", model="deepseek-chat",
        evidence_retriever=retriever,
    )

    source_id = await service.record_user_evidence(
        "user-a", "run-1", "Reduced latency by 20%."
    )

    assert retriever.indexed == [{
        "owner": "user-a", "run_id": "run-1", "source_type": "user_evidence",
        "source_id": source_id, "content": "Reduced latency by 20%.",
    }]


class Input(BaseModel):
    value: str


class Output(BaseModel):
    value: str


async def echo(arguments, context: ToolContext):
    assert context.owner == "user-a"
    return Output(value=arguments.value)


class ToolLlm:
    provider_name = "deepseek"
    model = "deepseek-chat"

    def __init__(self):
        self.calls = 0

    async def complete(self, messages, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return LlmResult(None, "tool_calls", (ToolRequest("1", "echo", {"value": "ok"}),))
        return LlmResult("done", "stop")


async def test_bounded_loop_exposes_only_state_allowed_tools_and_returns_text():
    registry = ToolRegistry([ToolSpec("echo", Input, Output, ToolEffect.READ, {"ready"}, echo)])
    service = TailoringOrchestrator(Repository(), provider="deepseek", model="deepseek-chat",
                                    llm=ToolLlm(), tools=registry, max_turns=3, max_tool_calls=2)

    result = await service.run_loop([], state="ready", owner="user-a", run_id="run-1")

    assert result == "done"


async def test_bounded_loop_stops_runaway_tool_calls():
    llm = ToolLlm()
    llm.complete = lambda messages, **kwargs: _tool_result()
    registry = ToolRegistry([ToolSpec("echo", Input, Output, ToolEffect.READ, {"ready"}, echo)])
    service = TailoringOrchestrator(Repository(), provider="deepseek", model="deepseek-chat",
                                    llm=llm, tools=registry, max_turns=2, max_tool_calls=1)

    with pytest.raises(RuntimeError, match="tool-call limit"):
        await service.run_loop([], state="ready", owner="user-a", run_id="run-1")


async def _tool_result():
    return LlmResult(None, "tool_calls", (ToolRequest("1", "echo", {"value": "ok"}),))
