"""Application contract for evidence retrieval."""

from typing import Any, Protocol, TypedDict


class EvidenceMatch(TypedDict):
    content: str
    source_type: str
    source_id: str
    score: float
    metadata: dict[str, Any]


class EvidenceRetriever(Protocol):
    async def index(
        self,
        *,
        owner: str,
        run_id: str,
        source_type: str,
        source_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None: ...

    async def retrieve(
        self, query: str, *, owner: str, run_id: str, top_k: int = 5
    ) -> list[EvidenceMatch]: ...
