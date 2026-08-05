import pytest

from agent_service.infra.vector.postgres_evidence_retriever import PostgresEvidenceRetriever


def test_postgres_retriever_rejects_non_postgres_session_factory():
    class Bind:
        dialect = type("Dialect", (), {"name": "sqlite"})()

    class Factory:
        kw = {"bind": Bind()}

    with pytest.raises(ValueError, match="PostgreSQL"):
        PostgresEvidenceRetriever(Factory(), knowledge_dir=None)
