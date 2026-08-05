"""Local evidence index backed by the development vector store."""

from pathlib import Path
from typing import Any

from ...application.ports.retrieval import EvidenceMatch
from .evidence_common import EvidenceEmbedder, evidence_id, iter_knowledge_documents
from .simple_vector_store import SimpleVectorStore


class LocalEvidenceRetriever:
    """Indexes curated knowledge and owner-scoped evidence without external services."""

    def __init__(self, store: SimpleVectorStore, knowledge_dir: Path) -> None:
        self._store = store
        self._embedder = EvidenceEmbedder()
        self._index_knowledge(knowledge_dir)

    async def index(
        self,
        *,
        owner: str,
        run_id: str,
        source_type: str,
        source_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._add(
            content=content,
            source_type=source_type,
            source_id=source_id,
            scope="owner",
            owner=owner,
            run_id=run_id,
            metadata=metadata,
        )

    async def retrieve(
        self, query: str, *, owner: str, run_id: str, top_k: int = 5
    ) -> list[EvidenceMatch]:
        query_vector = self._embedder.embed(query)
        candidates = self._store.search(
            query_vector, top_k=top_k, filter_payload={"scope": "global"}
        )
        candidates += self._store.search(
            query_vector,
            top_k=top_k,
            filter_payload={"scope": "owner", "owner": owner, "run_id": run_id},
        )
        candidates.sort(key=lambda item: item["score"], reverse=True)
        return [self._match(item) for item in candidates[:top_k]]

    def _index_knowledge(self, knowledge_dir: Path) -> None:
        for source_id, content in iter_knowledge_documents(knowledge_dir):
            self._add(
                content=content, source_type="knowledge",
                source_id=source_id, scope="global",
            )

    def _add(
        self,
        *,
        content: str,
        source_type: str,
        source_id: str,
        scope: str,
        owner: str | None = None,
        run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "content": content,
            "source_type": source_type,
            "source_id": source_id,
            "scope": scope,
            "owner": owner,
            "run_id": run_id,
            "metadata": metadata or {},
        }
        self._store.add_vector(
            evidence_id(scope, owner, run_id, source_type, source_id),
            self._embedder.embed(content),
            payload,
        )

    @staticmethod
    def _match(item: dict[str, Any]) -> EvidenceMatch:
        payload = item["payload"]
        return {
            "content": payload["content"],
            "source_type": payload["source_type"],
            "source_id": payload["source_id"],
            "score": item["score"],
            "metadata": payload["metadata"],
        }
