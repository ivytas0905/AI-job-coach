from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from agent_service.api.auth import UserContext, get_current_user
from agent_service.infra.storage.workflow_repository import ResourceNotFoundError, StaleRevisionError
from agent_service.main import create_app
from agent_service.wiring import get_tailoring_orchestrator, get_workflow_repository


def run_record(**values):
    defaults = dict(
        id="run-1", state="awaiting_resume", revision=1, provider="deepseek",
        model="deepseek-chat", current_version_id=None, created_at=datetime(2026, 8, 5),
    )
    return SimpleNamespace(**{**defaults, **values})


def snapshot(run=None, *, events=()):
    return SimpleNamespace(
        run=run or run_record(), master_resume=None, job_description=None,
        messages=[], proposals=[], decisions=[], versions=[],
        exports=[], events=list(events),
    )


class Repository:
    async def list_runs(self, owner, *, limit, before):
        assert owner == "user-a"
        return [run_record()], None

    async def load_run(self, owner, run_id):
        assert owner == "user-a"
        return snapshot()

    async def events_after(self, owner, run_id, sequence):
        assert owner == "user-a"
        assert sequence == 4
        return [SimpleNamespace(sequence=5, event_type="snapshot_changed")]


class Orchestrator:
    def __init__(self, repository):
        self.repository = repository

    async def create_run(self, owner):
        assert owner == "user-a"
        return run_record()


def client():
    application = create_app()
    repository = Repository()
    application.dependency_overrides[get_current_user] = lambda: UserContext(subject="user-a")
    application.dependency_overrides[get_workflow_repository] = lambda: repository
    application.dependency_overrides[get_tailoring_orchestrator] = lambda: Orchestrator(repository)
    return TestClient(application)


def test_create_list_and_reload_authoritative_run_snapshot():
    api = client()

    created = api.post("/api/v1/agent/runs")
    listed = api.get("/api/v1/agent/runs")
    reloaded = api.get("/api/v1/agent/runs/run-1")

    assert created.status_code == 201
    assert created.json()["run"]["id"] == "run-1"
    assert listed.json()["items"][0]["provider"] == "deepseek"
    assert reloaded.json()["latest_event_sequence"] == 0


def test_sse_reconnect_emits_only_events_after_authenticated_cursor():
    response = client().get("/api/v1/agent/runs/run-1/events?after=4")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "id: 5" in response.text
    assert '"sequence": 5' in response.text
    assert "authorization" not in response.text.lower()


def test_resume_upload_rejects_empty_unsupported_and_mismatched_files():
    api = client()

    empty = api.post("/api/v1/agent/runs/run-1/resume", files={"file": ("resume.pdf", b"", "application/pdf")})
    unsupported = api.post("/api/v1/agent/runs/run-1/resume", files={"file": ("resume.txt", b"hello", "text/plain")})
    mismatch = api.post("/api/v1/agent/runs/run-1/resume", files={"file": ("resume.pdf", b"not a pdf", "application/pdf")})

    assert empty.status_code == 400
    assert unsupported.status_code == 400
    assert mismatch.status_code == 400


def test_foreign_run_is_indistinguishable_from_missing_run():
    class HiddenRepository(Repository):
        async def load_run(self, owner, run_id):
            raise ResourceNotFoundError("foreign")

    application = create_app()
    hidden = HiddenRepository()
    application.dependency_overrides[get_current_user] = lambda: UserContext(subject="user-b")
    application.dependency_overrides[get_workflow_repository] = lambda: hidden

    response = TestClient(application).get("/api/v1/agent/runs/run-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found"}


def test_stale_proposal_decision_returns_stable_conflict():
    class StaleOrchestrator(Orchestrator):
        async def decide_proposal(self, owner, run_id, proposal_id, **values):
            raise StaleRevisionError("Proposal revision is no longer current")

    application = create_app()
    repository = Repository()
    application.dependency_overrides[get_current_user] = lambda: UserContext(subject="user-a")
    application.dependency_overrides[get_tailoring_orchestrator] = lambda: StaleOrchestrator(repository)

    response = TestClient(application).post(
        "/api/v1/agent/runs/run-1/proposals/proposal-1/decisions",
        json={"decision": "rejected", "expected_revision": 1,
              "idempotency_key": "decision-key"},
    )

    assert response.status_code == 409
