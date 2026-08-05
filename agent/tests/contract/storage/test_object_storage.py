import pytest

from agent_service.infra.storage.object_store import (
    LocalObjectStorage,
    ObjectStorageError,
    S3ObjectStorage,
)


class FakeBody:
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content


class FakeS3Client:
    def __init__(self):
        self.objects = {}

    def put_object(self, **kwargs):
        self.objects[kwargs["Key"]] = kwargs

    def get_object(self, **kwargs):
        stored = self.objects[kwargs["Key"]]
        return {"Body": FakeBody(stored["Body"]), "Metadata": stored["Metadata"]}

    def delete_object(self, **kwargs):
        self.objects.pop(kwargs["Key"], None)


@pytest.mark.asyncio
async def test_local_adapter_round_trips_owned_object(tmp_path):
    storage = LocalObjectStorage(tmp_path, max_size_bytes=16)

    stored = await storage.put(
        "user-a", "exports/resume.pdf", b"pdf", "application/pdf"
    )

    assert stored.key == "user-a/exports/resume.pdf"
    assert await storage.get("user-a", stored.key) == b"pdf"


@pytest.mark.asyncio
async def test_local_adapter_rejects_foreign_unsafe_oversized_and_wrong_type(tmp_path):
    storage = LocalObjectStorage(
        tmp_path,
        max_size_bytes=4,
        allowed_content_types={"application/pdf"},
    )
    stored = await storage.put("user-a", "resume.pdf", b"pdf", "application/pdf")

    with pytest.raises(ObjectStorageError):
        await storage.get("user-b", stored.key)
    with pytest.raises(ObjectStorageError):
        await storage.put("user-a", "../escape.pdf", b"pdf", "application/pdf")
    with pytest.raises(ObjectStorageError):
        await storage.put("user-a", "large.pdf", b"12345", "application/pdf")
    with pytest.raises(ObjectStorageError):
        await storage.put("user-a", "resume.exe", b"x", "application/octet-stream")
    with pytest.raises(ObjectStorageError):
        await storage.put("user-a", "user-a", b"pdf", "application/pdf")
    with pytest.raises(ObjectStorageError):
        await storage.put("user-a", "empty.pdf", b"", "application/pdf")


@pytest.mark.asyncio
async def test_s3_compatible_adapter_preserves_owner_metadata():
    client = FakeS3Client()
    storage = S3ObjectStorage(client, "resume-files", max_size_bytes=16)

    stored = await storage.put(
        "user-a", "exports/resume.pdf", b"pdf", "application/pdf"
    )

    assert client.objects[stored.key]["Metadata"] == {"owner": "user-a"}
    assert await storage.get("user-a", stored.key) == b"pdf"
    with pytest.raises(ObjectStorageError):
        await storage.get("user-b", stored.key)
