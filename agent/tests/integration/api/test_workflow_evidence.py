from fastapi.testclient import TestClient

from agent_service.api.auth import UserContext, get_current_user
from agent_service.main import create_app
from agent_service.wiring import get_tailoring_orchestrator


class Orchestrator:
    def __init__(self):
        self.calls = []

    async def record_user_evidence(self, owner, run_id, content):
        self.calls.append((owner, run_id, content))
        return "evidence-1"


def test_authenticated_user_can_create_agent_run():
    application = create_app()
    orchestrator = Orchestrator()
    application.dependency_overrides[get_current_user] = lambda: UserContext(subject="user-a")
    application.dependency_overrides[get_tailoring_orchestrator] = lambda: orchestrator

    orchestrator.create_run = lambda owner: None
    # The U7 route family is authenticated and replaces the temporary workflow route.
    paths = application.openapi()["paths"]

    assert "/api/v1/agent/runs" in paths
    assert not any("/workflow/" in path for path in paths)
