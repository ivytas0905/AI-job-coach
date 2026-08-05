"""Ownership-aware durable object storage contract."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StoredObject:
    key: str
    content_type: str
    size_bytes: int


class ObjectStorage(Protocol):
    async def put(
        self,
        owner: str,
        key: str,
        content: bytes,
        content_type: str,
    ) -> StoredObject: ...

    async def get(self, owner: str, key: str) -> bytes: ...

    async def delete(self, owner: str, key: str) -> None: ...
