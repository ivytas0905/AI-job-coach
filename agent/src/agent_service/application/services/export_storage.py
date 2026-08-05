"""Coordinate durable export content and relational metadata."""

from typing import Any

from ..ports.object_storage import ObjectStorage


class ExportStorageService:
    def __init__(self, storage: ObjectStorage, repository: Any) -> None:
        self.storage = storage
        self.repository = repository

    async def persist_export(
        self,
        *,
        owner: str,
        run_id: str,
        version_id: str,
        key: str,
        content: bytes,
        content_type: str,
    ):
        stored = await self.storage.put(owner, key, content, content_type)
        try:
            return await self.repository.create_export(
                owner=owner,
                run_id=run_id,
                version_id=version_id,
                storage_key=stored.key,
                content_type=stored.content_type,
                size_bytes=stored.size_bytes,
            )
        except Exception:
            await self.storage.delete(owner, stored.key)
            raise
