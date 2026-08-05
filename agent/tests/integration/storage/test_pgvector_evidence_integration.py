import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from agent_service.infra.storage.database import DatabaseManager
from agent_service.infra.vector.postgres_evidence_retriever import PostgresEvidenceRetriever


pytestmark = pytest.mark.postgres
PROJECT_ROOT = Path(__file__).parents[3]


async def test_pgvector_persists_evidence_and_enforces_owner_scope(tmp_path):
    database_url = os.getenv("RESUME_TEST_POSTGRES_URL")
    if not database_url:
        pytest.skip("RESUME_TEST_POSTGRES_URL is not configured")

    config = Config(PROJECT_ROOT / "alembic.ini")
    config.set_main_option(
        "sqlalchemy.url",
        database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://"),
    )
    command.upgrade(config, "head")
    database = DatabaseManager(database_url)
    async with database.async_session_factory() as session:
        await session.execute(text("DELETE FROM evidence_vectors"))
        await session.commit()

    retriever = PostgresEvidenceRetriever(database.async_session_factory, tmp_path)
    await retriever.index(
        owner="user-a", source_type="user_evidence", source_id="owned",
        run_id="run-a",
        content="Built a Python data pipeline.",
    )
    await retriever.index(
        owner="user-a", source_type="user_evidence", source_id="other-run",
        run_id="run-b",
        content="Built a private Python trading platform.",
    )

    matches = await retriever.retrieve(
        "Python platform", owner="user-a", run_id="run-a", top_k=10
    )

    assert {item["source_id"] for item in matches} == {"owned"}
    await database.close()
