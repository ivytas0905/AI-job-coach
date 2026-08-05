"""Persistent PostgreSQL/pgvector evidence retrieval adapter."""

import asyncio
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from sqlalchemy import text

from ...application.ports.retrieval import EvidenceMatch
from .evidence_common import EvidenceEmbedder, evidence_id, iter_knowledge_documents


class PostgresEvidenceRetriever:
    def __init__(self, session_factory, knowledge_dir: Path | None) -> None:
        bind = getattr(session_factory, "kw", {}).get("bind")
        if bind is None or bind.dialect.name != "postgresql":
            raise ValueError("PostgresEvidenceRetriever requires PostgreSQL")
        self._sessions = session_factory
        self._knowledge_dir = knowledge_dir
        documents = list(iter_knowledge_documents(knowledge_dir))
        corpus = "\n".join(f"{name}\0{content}" for name, content in documents)
        self._knowledge_documents = documents
        self._corpus_version = sha256(corpus.encode()).hexdigest()
        self._embedder = EvidenceEmbedder()
        self._seed_lock = asyncio.Lock()
        self._seeded = False

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
        await self._ensure_knowledge_indexed()
        await self._upsert(
            owner=owner, run_id=run_id, scope="owner", source_type=source_type,
            source_id=source_id, content=content, metadata=metadata or {},
        )

    async def retrieve(
        self, query: str, *, owner: str, run_id: str, top_k: int = 5
    ) -> list[EvidenceMatch]:
        await self._ensure_knowledge_indexed()
        statement = text(
            "SELECT content, source_type, source_id, metadata, "
            "1 - (embedding <=> CAST(:embedding AS vector)) AS score "
            "FROM evidence_vectors "
            "WHERE (scope = 'global' AND metadata->>'corpus_version' = :corpus_version) "
            "OR (scope = 'owner' AND owner_id = :owner AND run_id = :run_id) "
            "ORDER BY embedding <=> CAST(:embedding AS vector) LIMIT :top_k"
        )
        async with self._sessions() as session:
            rows = (await session.execute(statement, {
                "embedding": self._embedder.vector_literal(query),
                "owner": owner,
                "run_id": run_id,
                "corpus_version": self._corpus_version,
                "top_k": top_k,
            })).mappings().all()
        return [
            {
                "content": row["content"], "source_type": row["source_type"],
                "source_id": row["source_id"], "score": float(row["score"]),
                "metadata": row["metadata"],
            }
            for row in rows
        ]

    async def _ensure_knowledge_indexed(self) -> None:
        if self._seeded:
            return
        async with self._seed_lock:
            if self._seeded:
                return
            for source_id, content in self._knowledge_documents:
                await self._upsert(
                    owner=None, run_id=None, scope="global", source_type="knowledge",
                    source_id=source_id, content=content,
                    metadata={"corpus_version": self._corpus_version},
                    identity_version=self._corpus_version,
                )
            self._seeded = True

    async def _upsert(
        self, *, owner: str | None, run_id: str | None, scope: str, source_type: str,
        source_id: str, content: str, metadata: dict[str, Any],
        identity_version: str | None = None,
    ) -> None:
        statement = text(
            "INSERT INTO evidence_vectors "
            "(id, owner_id, run_id, scope, source_type, source_id, content, metadata, embedding) "
            "VALUES (:id, :owner, :run_id, :scope, :source_type, :source_id, :content, "
            "CAST(:metadata AS jsonb), CAST(:embedding AS vector)) "
            "ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, "
            "metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding "
            "WHERE evidence_vectors.content IS DISTINCT FROM EXCLUDED.content "
            "OR evidence_vectors.metadata IS DISTINCT FROM EXCLUDED.metadata"
        )
        async with self._sessions() as session:
            await session.execute(statement, {
                "id": evidence_id(
                    scope, owner, identity_version or run_id, source_type, source_id
                ),
                "owner": owner, "run_id": run_id, "scope": scope,
                "source_type": source_type, "source_id": source_id, "content": content,
                "metadata": json.dumps(metadata),
                "embedding": self._embedder.vector_literal(content),
            })
            await session.commit()
