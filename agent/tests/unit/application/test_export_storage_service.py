import pytest

from agent_service.application.services.export_storage import ExportStorageService
from agent_service.application.ports.object_storage import StoredObject


class RecordingStorage:
    def __init__(self):
        self.deleted = []

    async def put(self, owner, key, content, content_type):
        return StoredObject(
            key=f"{owner}/{key}", content_type=content_type, size_bytes=len(content)
        )

    async def delete(self, owner, key):
        self.deleted.append((owner, key))


class FailingRepository:
    async def create_export(self, **kwargs):
        raise RuntimeError("metadata commit failed")


@pytest.mark.asyncio
async def test_failed_metadata_commit_removes_uploaded_export():
    storage = RecordingStorage()
    service = ExportStorageService(storage, FailingRepository())

    with pytest.raises(RuntimeError, match="metadata commit failed"):
        await service.persist_export(
            owner="user-a",
            run_id="run-a",
            version_id="version-a",
            key="exports/resume.pdf",
            content=b"pdf",
            content_type="application/pdf",
        )

    assert storage.deleted == [("user-a", "user-a/exports/resume.pdf")]
