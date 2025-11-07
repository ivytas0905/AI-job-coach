"""
Simple In-Memory Vector Store for Semantic Search.

This is a numpy-based implementation for development.
Can be upgraded to Qdrant for production by implementing the same interface.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass
from threading import Lock


@dataclass
class VectorEntry:
    """Entry in the vector store."""
    id: str
    vector: List[float]
    payload: Dict[str, Any]


class SimpleVectorStore:
    """
    Simple in-memory vector store with cosine similarity search.

    Features:
    - Cosine similarity based search
    - Metadata filtering
    - User-based partitioning
    - Thread-safe operations

    This provides a simplified interface similar to Qdrant.
    """

    def __init__(self):
        """Initialize vector store."""
        self._vectors: Dict[str, VectorEntry] = {}
        self._lock = Lock()

    def add_vector(
        self,
        id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ):
        """
        Add a single vector to the store.

        Args:
            id: Unique identifier for the vector
            vector: Embedding vector (list of floats)
            payload: Metadata associated with the vector
        """
        with self._lock:
            self._vectors[id] = VectorEntry(
                id=id,
                vector=vector,
                payload=payload
            )

    def add_vectors_batch(self, entries: List[Dict[str, Any]]):
        """
        Add multiple vectors in batch.

        Args:
            entries: List of dicts with keys: id, vector, payload
        """
        with self._lock:
            for entry in entries:
                self._vectors[entry['id']] = VectorEntry(
                    id=entry['id'],
                    vector=entry['vector'],
                    payload=entry.get('payload', {})
                )

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_payload: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using cosine similarity.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_payload: Optional filter on payload fields (e.g., {"user_id": "123"})

        Returns:
            List of results sorted by similarity score (highest first)
            Each result: {"id": str, "score": float, "payload": dict}
        """
        with self._lock:
            # Filter vectors based on payload
            candidates = self._vectors.values()

            if filter_payload:
                candidates = [
                    entry for entry in candidates
                    if self._matches_filter(entry.payload, filter_payload)
                ]

            if not candidates:
                return []

            # Calculate cosine similarity for all candidates
            query_norm = np.linalg.norm(query_vector)
            results = []

            for entry in candidates:
                # Cosine similarity = dot product / (norm1 * norm2)
                score = self._cosine_similarity(query_vector, entry.vector, query_norm)

                results.append({
                    "id": entry.id,
                    "score": float(score),
                    "payload": entry.payload
                })

            # Sort by score (descending)
            results.sort(key=lambda x: x["score"], reverse=True)

            # Return top K
            return results[:top_k]

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float],
        vec1_norm: Optional[float] = None
    ) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector
            vec1_norm: Pre-calculated norm of vec1 (optimization)

        Returns:
            Cosine similarity score (-1 to 1)
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        # Dot product
        dot_product = np.dot(vec1_np, vec2_np)

        # Norms
        norm1 = vec1_norm if vec1_norm is not None else np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _matches_filter(
        self,
        payload: Dict[str, Any],
        filter_payload: Dict[str, Any]
    ) -> bool:
        """
        Check if payload matches filter criteria.

        Args:
            payload: Entry payload
            filter_payload: Filter criteria

        Returns:
            True if all filter conditions match
        """
        for key, value in filter_payload.items():
            if payload.get(key) != value:
                return False
        return True

    def delete_by_id(self, id: str):
        """
        Delete vector by ID.

        Args:
            id: Vector ID to delete
        """
        with self._lock:
            if id in self._vectors:
                del self._vectors[id]

    def delete_by_filter(self, filter_payload: Dict[str, Any]):
        """
        Delete all vectors matching filter.

        Args:
            filter_payload: Filter criteria
        """
        with self._lock:
            to_delete = [
                id for id, entry in self._vectors.items()
                if self._matches_filter(entry.payload, filter_payload)
            ]

            for id in to_delete:
                del self._vectors[id]

    def clear(self):
        """Clear all vectors from store."""
        with self._lock:
            self._vectors.clear()

    def count(self, filter_payload: Optional[Dict[str, Any]] = None) -> int:
        """
        Count vectors in store.

        Args:
            filter_payload: Optional filter criteria

        Returns:
            Number of vectors matching filter (or total if no filter)
        """
        with self._lock:
            if filter_payload is None:
                return len(self._vectors)

            return sum(
                1 for entry in self._vectors.values()
                if self._matches_filter(entry.payload, filter_payload)
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dictionary with stats (total_vectors, vector_dimension, etc.)
        """
        with self._lock:
            if not self._vectors:
                return {
                    "total_vectors": 0,
                    "vector_dimension": 0,
                    "store_type": "simple_memory"
                }

            # Get dimension from first vector
            first_entry = next(iter(self._vectors.values()))
            dimension = len(first_entry.vector)

            return {
                "total_vectors": len(self._vectors),
                "vector_dimension": dimension,
                "store_type": "simple_memory"
            }


# Singleton instance
_vector_store_instance: Optional[SimpleVectorStore] = None


def get_vector_store() -> SimpleVectorStore:
    """
    Get singleton vector store instance.

    Returns:
        SimpleVectorStore instance
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = SimpleVectorStore()
    return _vector_store_instance


# Future: Qdrant implementation (same interface)
"""
class QdrantVectorStore:
    '''Qdrant-based vector store (for production)'''

    def __init__(self, qdrant_url: str, collection_name: str):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name

        # Create collection if not exists
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )

    def add_vector(self, id: str, vector: List[float], payload: Dict[str, Any]):
        from qdrant_client.models import PointStruct

        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=id, vector=vector, payload=payload)]
        )

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_payload: Optional[Dict[str, Any]] = None
    ):
        query_filter = None
        if filter_payload:
            from qdrant_client.models import FieldCondition, Filter
            query_filter = Filter(
                must=[
                    FieldCondition(key=k, match={"value": v})
                    for k, v in filter_payload.items()
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k
        )

        return [
            {"id": hit.id, "score": hit.score, "payload": hit.payload}
            for hit in results
        ]
"""
