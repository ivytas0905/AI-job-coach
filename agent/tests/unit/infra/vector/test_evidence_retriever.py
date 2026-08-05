from pathlib import Path

from agent_service.infra.vector.evidence_retriever import LocalEvidenceRetriever
from agent_service.infra.vector.simple_vector_store import SimpleVectorStore


async def test_retrieval_combines_global_knowledge_with_only_owned_evidence(tmp_path: Path):
    (tmp_path / "guidance.md").write_text(
        "Use verified Python project evidence.", encoding="utf-8"
    )
    retriever = LocalEvidenceRetriever(SimpleVectorStore(), tmp_path)
    await retriever.index(
        owner="user-a",
        run_id="run-a",
        source_type="resume_bullet",
        source_id="bullet-a",
        content="Built a Python data pipeline.",
    )
    await retriever.index(
        owner="user-a",
        run_id="run-b",
        source_type="resume_bullet",
        source_id="other-run",
        content="Built a secret Python trading system.",
    )

    matches = await retriever.retrieve(
        "Python project", owner="user-a", run_id="run-a", top_k=10
    )

    assert {item["source_id"] for item in matches} == {"guidance.md", "bullet-a"}
    assert all({"content", "source_type", "source_id", "score", "metadata"} == set(item)
               for item in matches)


async def test_retrieval_returns_results_in_descending_similarity_order(tmp_path: Path):
    retriever = LocalEvidenceRetriever(SimpleVectorStore(), tmp_path)
    await retriever.index(
        owner="user-a", source_type="resume_bullet", source_id="exact",
        run_id="run-a",
        content="Python data pipeline",
    )
    await retriever.index(
        owner="user-a", source_type="resume_bullet", source_id="other",
        run_id="run-a",
        content="Customer support operations",
    )

    matches = await retriever.retrieve(
        "Python data pipeline", owner="user-a", run_id="run-a"
    )

    assert matches[0]["source_id"] == "exact"
    assert matches[0]["score"] >= matches[1]["score"]
