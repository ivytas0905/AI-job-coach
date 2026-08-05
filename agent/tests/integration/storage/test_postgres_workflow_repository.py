import os

import pytest

from agent_service.infra.storage.database import Base, DatabaseManager
from agent_service.infra.storage.models import MasterResumeModel
from agent_service.infra.storage.workflow_repository import WorkflowRepository


pytestmark = pytest.mark.postgres


@pytest.mark.asyncio
async def test_postgres_owner_reload_round_trip():
    database_url = os.getenv("RESUME_TEST_POSTGRES_URL")
    if not database_url:
        pytest.skip("RESUME_TEST_POSTGRES_URL is not configured")
    database = DatabaseManager(database_url)
    async with database.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    repository = WorkflowRepository(database.async_session_factory)
    async with database.async_session_factory() as session:
        session.add(
            MasterResumeModel(
                id="postgres-master",
                user_id="postgres-user",
                filename="resume.pdf",
                parsed_data={},
            )
        )
        await session.commit()

    run = await repository.create_run(
        "postgres-user",
        provider="deepseek",
        model="deepseek-chat",
        master_resume_id="postgres-master",
    )

    assert (await repository.load_run("postgres-user", run.id)).run.id == run.id
    await database.close()
