"""Filesystem and S3-compatible object storage adapters."""

import asyncio
from pathlib import Path, PurePosixPath
from typing import Any

from ...application.ports.object_storage import StoredObject


class ObjectStorageError(ValueError):
    pass


class StorageValidationMixin:
    def __init__(
        self,
        *,
        max_size_bytes: int,
        allowed_content_types: set[str] | None = None,
    ) -> None:
        self.max_size_bytes = max_size_bytes
        self.allowed_content_types = allowed_content_types or {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

    def owned_key(self, owner: str, key: str) -> str:
        if not owner or "/" in owner or "\\" in owner:
            raise ObjectStorageError("Invalid object owner")
        path = PurePosixPath(key.replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ObjectStorageError("Invalid object key")
        if path.parts[0] == owner:
            if len(path.parts) == 1:
                raise ObjectStorageError("Object key must include a filename")
            return path.as_posix()
        if len(path.parts) > 1 and path.parts[0].startswith("user-"):
            raise ObjectStorageError("Object belongs to another owner")
        return (PurePosixPath(owner) / path).as_posix()

    def validate_write(self, content: bytes, content_type: str) -> None:
        if not content:
            raise ObjectStorageError("Object content cannot be empty")
        if len(content) > self.max_size_bytes:
            raise ObjectStorageError("Object exceeds configured size limit")
        if content_type not in self.allowed_content_types:
            raise ObjectStorageError("Unsupported object content type")


class LocalObjectStorage(StorageValidationMixin):
    def __init__(
        self,
        root: str | Path,
        *,
        max_size_bytes: int,
        allowed_content_types: set[str] | None = None,
    ) -> None:
        super().__init__(
            max_size_bytes=max_size_bytes,
            allowed_content_types=allowed_content_types,
        )
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, owner: str, key: str) -> tuple[str, Path]:
        owned_key = self.owned_key(owner, key)
        path = (self.root / Path(*PurePosixPath(owned_key).parts)).resolve()
        if self.root not in path.parents:
            raise ObjectStorageError("Object key escapes storage root")
        return owned_key, path

    async def put(
        self, owner: str, key: str, content: bytes, content_type: str
    ) -> StoredObject:
        self.validate_write(content, content_type)
        owned_key, path = self._path(owner, key)
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, content)
        return StoredObject(owned_key, content_type, len(content))

    async def get(self, owner: str, key: str) -> bytes:
        _, path = self._path(owner, key)
        try:
            return await asyncio.to_thread(path.read_bytes)
        except FileNotFoundError as exc:
            raise ObjectStorageError("Object not found") from exc

    async def delete(self, owner: str, key: str) -> None:
        _, path = self._path(owner, key)
        try:
            await asyncio.to_thread(path.unlink)
        except FileNotFoundError:
            return


class S3ObjectStorage(StorageValidationMixin):
    """Thin async wrapper around a boto3-compatible client."""

    def __init__(
        self,
        client: Any,
        bucket: str,
        *,
        max_size_bytes: int,
        allowed_content_types: set[str] | None = None,
    ) -> None:
        super().__init__(
            max_size_bytes=max_size_bytes,
            allowed_content_types=allowed_content_types,
        )
        if not bucket:
            raise ObjectStorageError("S3 bucket is required")
        self.client = client
        self.bucket = bucket

    async def put(
        self, owner: str, key: str, content: bytes, content_type: str
    ) -> StoredObject:
        self.validate_write(content, content_type)
        owned_key = self.owned_key(owner, key)
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=owned_key,
            Body=content,
            ContentType=content_type,
            Metadata={"owner": owner},
        )
        return StoredObject(owned_key, content_type, len(content))

    async def get(self, owner: str, key: str) -> bytes:
        owned_key = self.owned_key(owner, key)
        response = await asyncio.to_thread(
            self.client.get_object, Bucket=self.bucket, Key=owned_key
        )
        metadata = response.get("Metadata", {})
        if metadata.get("owner") != owner:
            raise ObjectStorageError("Object belongs to another owner")
        return await asyncio.to_thread(response["Body"].read)

    async def delete(self, owner: str, key: str) -> None:
        owned_key = self.owned_key(owner, key)
        await asyncio.to_thread(
            self.client.delete_object, Bucket=self.bucket, Key=owned_key
        )
