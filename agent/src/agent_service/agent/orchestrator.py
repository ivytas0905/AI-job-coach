"""Application boundary for persisted workflow commands."""

import json
from hashlib import sha256
from uuid import uuid4

from ..application.ports.llm import LlmMessage
from ..infra.storage.workflow_repository import (
    ResourceNotFoundError,
    StaleRevisionError,
)
from .state_machine import WorkflowStateMachine


class TailoringOrchestrator:
    def __init__(self, repository, *, provider: str, model: str, llm=None, tools=None,
                 evidence_retriever=None,
                 max_turns: int = 6, max_tool_calls: int = 8) -> None:
        self.repository = repository
        self.provider = provider
        self.model = model
        self.states = WorkflowStateMachine()
        self.llm = llm
        self.tools = tools
        self.evidence_retriever = evidence_retriever
        self.max_turns = max_turns
        self.max_tool_calls = max_tool_calls

    async def create_run(self, owner: str, **sources):
        return await self.repository.create_run(
            owner, provider=self.provider, model=self.model, **sources
        )

    async def record_event(self, owner: str, run_id: str, event: str, state: str):
        new_state = self.states.transition(state, event)
        return await self.repository.transition_run(
            owner, run_id, expected_state=state, new_state=new_state
        )

    async def record_user_evidence(self, owner: str, run_id: str, content: str) -> str:
        """Persist evidence supplied through an authenticated user command boundary."""
        if self.evidence_retriever is None:
            raise RuntimeError("Evidence retriever is required")
        await self.repository.load_run(owner, run_id)
        source_id = sha256(content.encode()).hexdigest()
        await self.evidence_retriever.index(
            owner=owner,
            run_id=run_id,
            source_type="user_evidence",
            source_id=source_id,
            content=content,
        )
        return source_id

    async def submit_resume(self, owner: str, run_id: str, filename: str, content: bytes):
        result = await self.tools.execute(
            "parse_resume", {"filename": filename, "content": content},
            state="awaiting_resume", owner=owner, run_id=run_id,
        )
        run = await self.repository.attach_master_resume(
            owner, run_id, filename=filename, parsed_data=result.resume
        )
        await self.repository.append_event(owner, run_id, "snapshot_changed", {"revision": run.revision})
        return run

    async def submit_job_description(self, owner: str, run_id: str, content: str):
        result = await self.tools.execute(
            "analyze_jd", {"text": content}, state="awaiting_jd",
            owner=owner, run_id=run_id,
        )
        run = await self.repository.attach_job_description(
            owner, run_id, raw_text=content, analysis=result.analysis,
            jd_hash=sha256(content.encode()).hexdigest(),
        )
        await self.repository.append_event(owner, run_id, "snapshot_changed", {"revision": run.revision})
        return run

    async def send_message(self, owner: str, run_id: str, content: str) -> str:
        snapshot = await self.repository.load_run(owner, run_id)
        await self.repository.append_message(owner, run_id, "user", content)
        messages = [LlmMessage(item.role, item.content) for item in snapshot.messages]
        messages.append(LlmMessage("user", content))
        response = await self.run_loop(
            messages, state=snapshot.run.state, owner=owner, run_id=run_id
        )
        await self.repository.append_message(owner, run_id, "assistant", response)
        await self.repository.append_event(owner, run_id, "snapshot_changed", {})
        return response

    async def decide_proposal(
        self, owner: str, run_id: str, proposal_id: str, **values
    ):
        snapshot = await self.repository.load_run(owner, run_id)
        if proposal_id not in {item.id for item in snapshot.proposals}:
            raise ResourceNotFoundError("Proposal not found")
        return await self.repository.decide_proposal(owner, proposal_id, **values)

    async def restore_version(
        self, owner: str, run_id: str, version_id: str, *, idempotency_key: str
    ):
        version = await self.repository.restore_version(
            owner, run_id, version_id, idempotency_key=idempotency_key
        )
        await self.repository.append_event(owner, run_id, "snapshot_changed", {})
        return version

    async def create_export(
        self, owner: str, run_id: str, version_id: str, format: str, export_storage,
        *, idempotency_key: str,
    ):
        content_type = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }[format]
        replay = await self.repository.get_export_by_idempotency_key(
            owner, run_id, idempotency_key
        )
        if replay is not None:
            if replay.version_id != version_id or replay.content_type != content_type:
                raise StaleRevisionError("Idempotency key was used for another export")
            return replay
        version = await self.repository.get_version(owner, run_id, version_id)
        generated = await self.tools.execute(
            "export_approved_resume", {"resume": version.content, "format": format},
            state="approved", owner=owner, run_id=run_id,
        )
        suffix = "docx" if format == "docx" else "pdf"
        record = await export_storage.persist_export(
            owner=owner, run_id=run_id, version_id=version_id,
            key=f"exports/{run_id}/{version_id}-{uuid4().hex}.{suffix}",
            content=generated.content,
            content_type=generated.content_type,
            idempotency_key=idempotency_key,
        )
        await self.repository.append_event(owner, run_id, "snapshot_changed", {})
        return record

    async def run_loop(self, messages, *, state: str, owner: str, run_id: str) -> str:
        if self.llm is None or self.tools is None:
            raise RuntimeError("LLM and tool registry are required")
        conversation = list(messages)
        tool_calls = 0
        schemas = [
            {"type": "function", "function": {
                "name": item["name"], "description": f"{item['effect']} capability",
                "parameters": item["input_schema"],
            }}
            for item in self.tools.describe(state)
        ]
        for _ in range(self.max_turns):
            result = await self.llm.complete(conversation, tools=schemas)
            if result.tool_requests:
                tool_calls += len(result.tool_requests)
                if tool_calls > self.max_tool_calls:
                    raise RuntimeError("Agent tool-call limit exceeded")
                conversation.append(LlmMessage(
                    role="assistant", content=result.text, tool_requests=result.tool_requests
                ))
                for request in result.tool_requests:
                    output = await self.tools.execute(
                        request.name, request.arguments, state=state,
                        owner=owner, run_id=run_id,
                    )
                    if request.name == "propose_tailoring":
                        for proposal in output.proposals:
                            await self.repository.create_proposal(
                                owner, run_id,
                                proposal.affected_content,
                                proposal.suggested_replacement,
                                proposal.jd_reason,
                                {"items": proposal.source_evidence},
                                proposal.evidence_request,
                            )
                        if state != "proposal_ready":
                            await self.repository.transition_run(
                                owner, run_id, expected_state=state,
                                new_state="proposal_ready",
                            )
                        await self.repository.append_event(
                            owner, run_id, "snapshot_changed", {}
                        )
                    conversation.append(LlmMessage(
                        role="tool", content=json.dumps(output.model_dump(mode="json")),
                        tool_call_id=request.id,
                    ))
                continue
            if result.text is not None:
                return result.text
            raise RuntimeError("Agent returned neither text nor tool calls")
        raise RuntimeError("Agent turn limit exceeded")
