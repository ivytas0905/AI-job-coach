from datetime import datetime

import pytest
from sqlalchemy import update

from agent_service.infra.storage.database import Base, DatabaseManager
from agent_service.infra.storage.models import (
    JDAnalysisModel,
    MasterResumeModel,
    TailoringRunModel,
)
from agent_service.infra.storage.workflow_repository import (
    ResourceNotFoundError,
    WorkflowRepository,
)


@pytest.fixture
async def repository(tmp_path):
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'workflow.db'}")
    async with database.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with database.async_session_factory() as session:
        session.add(
            MasterResumeModel(
                id="master-a",
                user_id="user-a",
                filename="resume.pdf",
                parsed_data={"name": "A", "summary": "old"},
            )
        )
        session.add(
            JDAnalysisModel(
                id="jd-b",
                user_id="user-b",
                job_title="Engineer",
                raw_text="Job description",
                analysis_result={},
            )
        )
        await session.commit()
    yield WorkflowRepository(database.async_session_factory)
    await database.close()


@pytest.mark.asyncio
async def test_full_owner_snapshot_reloads_normalized_records(repository):
    run = await repository.create_run(
        "user-a",
        provider="deepseek",
        model="deepseek-chat",
        master_resume_id="master-a",
    )
    await repository.append_message("user-a", run.id, "user", "Tailor this resume")
    proposal = await repository.create_proposal(
        "user-a",
        run.id,
        original_text="Built APIs",
        suggested_text="Built reliable APIs",
        rationale="Matches the JD",
        source_evidence={"bullet_id": "b1"},
    )
    await repository.append_event("user-a", run.id, "proposal_created", {"proposal_id": proposal.id})

    snapshot = await repository.load_run("user-a", run.id)

    assert snapshot.run.provider == "deepseek"
    assert snapshot.run.model == "deepseek-chat"
    assert [message.content for message in snapshot.messages] == ["Tailor this resume"]
    assert [item.id for item in snapshot.proposals] == [proposal.id]
    assert [(event.sequence, event.event_type) for event in snapshot.events] == [(1, "proposal_created")]
    assert snapshot.master_resume.filename == "resume.pdf"
    assert snapshot.job_description is None


@pytest.mark.asyncio
async def test_run_cursor_does_not_drop_runs_with_equal_timestamps(repository):
    runs = [
        await repository.create_run("user-a", provider="deepseek", model="deepseek-chat")
        for _ in range(3)
    ]
    async with repository.session_factory() as session, session.begin():
        await session.execute(update(TailoringRunModel).values(created_at=datetime(2026, 8, 5)))

    first_page, cursor = await repository.list_runs("user-a", limit=2)
    second_page, next_cursor = await repository.list_runs("user-a", limit=2, before=cursor)

    assert {item.id for item in first_page + second_page} == {item.id for item in runs}
    assert len(first_page) == 2
    assert len(second_page) == 1
    assert next_cursor is None


@pytest.mark.asyncio
async def test_rejection_records_decision_without_creating_version(repository):
    run = await repository.create_run(
        "user-a", provider="deepseek", model="deepseek-chat", master_resume_id="master-a"
    )
    proposal = await repository.create_proposal(
        "user-a", run.id, "old", "new", "reason", {"source": "master"}
    )

    result = await repository.decide_proposal(
        "user-a",
        proposal.id,
        decision="rejected",
        expected_revision=1,
        idempotency_key="reject-1",
    )

    assert result.version is None
    snapshot = await repository.load_run("user-a", run.id)
    assert [decision.decision for decision in snapshot.decisions] == ["rejected"]
    assert snapshot.versions == []


@pytest.mark.asyncio
async def test_restore_creates_new_current_version_and_preserves_history(repository):
    run = await repository.create_run(
        "user-a", provider="deepseek", model="deepseek-chat", master_resume_id="master-a"
    )
    first = await repository.create_version(
        "user-a", run.id, "Initial", {"summary": "first"}
    )
    await repository.create_version("user-a", run.id, "Second", {"summary": "second"})

    restored = await repository.restore_version(
        "user-a", run.id, first.id, idempotency_key="restore-first-version"
    )
    replay = await repository.restore_version(
        "user-a", run.id, first.id, idempotency_key="restore-first-version"
    )
    snapshot = await repository.load_run("user-a", run.id)

    assert restored.content == {"summary": "first"}
    assert restored.parent_version_id == first.id
    assert replay.id == restored.id
    assert len(snapshot.versions) == 3
    assert snapshot.run.current_version_id == restored.id


@pytest.mark.asyncio
async def test_foreign_resources_are_invisible(repository):
    run = await repository.create_run(
        "user-a", provider="deepseek", model="deepseek-chat", master_resume_id="master-a"
    )

    with pytest.raises(ResourceNotFoundError):
        await repository.load_run("user-b", run.id)


@pytest.mark.asyncio
async def test_foreign_jd_cannot_be_attached_to_run(repository):
    with pytest.raises(ResourceNotFoundError):
        await repository.create_run(
            "user-a",
            provider="deepseek",
            model="deepseek-chat",
            master_resume_id="master-a",
            jd_analysis_id="jd-b",
        )


@pytest.mark.asyncio
async def test_export_metadata_requires_owner_scoped_storage_key(repository):
    run = await repository.create_run(
        "user-a", provider="deepseek", model="deepseek-chat", master_resume_id="master-a"
    )
    version = await repository.create_version("user-a", run.id, "Version", {})

    with pytest.raises(ResourceNotFoundError):
        await repository.create_export(
            owner="user-a",
            run_id=run.id,
            version_id=version.id,
            storage_key="user-b/exports/resume.pdf",
            content_type="application/pdf",
            size_bytes=3,
        )


@pytest.mark.asyncio
async def test_invalid_decision_cannot_corrupt_proposal_state(repository):
    run = await repository.create_run(
        "user-a", provider="deepseek", model="deepseek-chat", master_resume_id="master-a"
    )
    proposal = await repository.create_proposal(
        "user-a", run.id, "old", "new", "reason", {"source": "master"}
    )

    with pytest.raises(ValueError, match="Unsupported proposal decision"):
        await repository.decide_proposal(
            "user-a",
            proposal.id,
            decision="ignored",
            expected_revision=1,
            idempotency_key="invalid-1",
        )


@pytest.mark.asyncio
async def test_acceptance_atomically_creates_one_version_and_replays(repository):
    run = await repository.create_run(
        "user-a", provider="deepseek", model="deepseek-chat", master_resume_id="master-a"
    )
    proposal = await repository.create_proposal(
        "user-a", run.id, "old", "new", "reason", {"source": "master"}
    )

    first = await repository.decide_proposal(
        "user-a", proposal.id, decision="accepted", expected_revision=1,
        idempotency_key="accept-1", version_name="Tailored",
    )
    replay = await repository.decide_proposal(
        "user-a", proposal.id, decision="accepted", expected_revision=1,
        idempotency_key="accept-1", version_name="Tailored",
    )

    snapshot = await repository.load_run("user-a", run.id)
    assert first.version.id == replay.version.id
    assert len(snapshot.decisions) == 1
    assert len(snapshot.versions) == 1
    assert first.version.content["summary"] == "new"
    assert snapshot.run.state == "version_ready"
