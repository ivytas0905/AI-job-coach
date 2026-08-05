import pytest

from agent_service.infra.storage.database import Base, DatabaseManager
from agent_service.infra.storage.models import JDAnalysisModel, MasterResumeModel
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
                parsed_data={"name": "A"},
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

    snapshot = await repository.load_run("user-a", run.id)

    assert snapshot.run.provider == "deepseek"
    assert snapshot.run.model == "deepseek-chat"
    assert [message.content for message in snapshot.messages] == ["Tailor this resume"]
    assert [item.id for item in snapshot.proposals] == [proposal.id]


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

    restored = await repository.restore_version("user-a", run.id, first.id)
    snapshot = await repository.load_run("user-a", run.id)

    assert restored.content == {"summary": "first"}
    assert restored.parent_version_id == first.id
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
