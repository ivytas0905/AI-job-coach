"""Shared evidence identity, corpus loading, and local embedding rules."""

from hashlib import sha256
from pathlib import Path
from typing import Iterator

from sklearn.feature_extraction.text import HashingVectorizer


EMBEDDING_DIMENSION = 384
SUPPORTED_KNOWLEDGE_SUFFIXES = frozenset({".json", ".md", ".txt"})


class EvidenceEmbedder:
    dimension = EMBEDDING_DIMENSION

    def __init__(self) -> None:
        self._vectorizer = HashingVectorizer(
            n_features=self.dimension,
            analyzer="char_wb",
            ngram_range=(2, 4),
            norm="l2",
        )

    def embed(self, content: str) -> list[float]:
        return self._vectorizer.transform([content]).toarray()[0].tolist()

    def vector_literal(self, content: str) -> str:
        return "[" + ",".join(str(value) for value in self.embed(content)) + "]"


def evidence_id(
    scope: str, owner: str | None, run_id: str | None,
    source_type: str, source_id: str,
) -> str:
    identity = f"{scope}:{owner or ''}:{run_id or ''}:{source_type}:{source_id}"
    return sha256(identity.encode()).hexdigest()


def iter_knowledge_documents(knowledge_dir: Path | None) -> Iterator[tuple[str, str]]:
    if knowledge_dir is None:
        return
    for path in sorted(knowledge_dir.glob("*")):
        if path.suffix.lower() not in SUPPORTED_KNOWLEDGE_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8")
        if content.strip():
            yield path.name, content
