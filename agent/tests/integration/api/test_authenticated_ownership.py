from collections.abc import Iterator
import re

import pytest
from fastapi.testclient import TestClient

from agent_service.api.auth import UserContext, get_current_user
from agent_service.api.routes import master, tailor
from agent_service.domain.models import MasterResume, TailoredResume
from agent_service.main import create_app


@pytest.fixture(autouse=True)
def clear_in_memory_stores() -> Iterator[None]:
    master.master_resumes.clear()
    tailor.tailored_resumes.clear()
    tailor.job_descriptions.clear()
    tailor.job_description_owners.clear()
    tailor.tailored_resume_owners.clear()
    yield
    master.master_resumes.clear()
    tailor.tailored_resumes.clear()
    tailor.job_descriptions.clear()
    tailor.job_description_owners.clear()
    tailor.tailored_resume_owners.clear()


def test_active_api_routes_require_authentication():
    client = TestClient(create_app())

    response = client.get("/api/v1/master/resume")

    assert response.status_code == 401


def test_every_active_api_operation_fails_closed_without_user_context():
    application = create_app()
    client = TestClient(application)
    api_operations = [
        (method, path)
        for path, path_item in application.openapi()["paths"].items()
        if path.startswith("/api/v1/")
        for method in path_item
    ]

    assert api_operations
    for method, path in api_operations:
        concrete_path = re.sub(r"\{[^}]+\}", "unknown", path)
        response = client.request(method, concrete_path, json={})
        assert response.status_code == 401, (method, path, response.text)


def test_master_resume_lookup_only_returns_verified_users_resource():
    application = create_app()
    application.dependency_overrides[get_current_user] = lambda: UserContext(subject="user_a")
    client = TestClient(application)
    master.master_resumes["a"] = MasterResume(id="a", user_id="user_a")
    master.master_resumes["b"] = MasterResume(id="b", user_id="user_b")

    response = client.get("/api/v1/master/resume")

    assert response.status_code == 200
    assert response.json()["id"] == "a"
    assert response.json()["user_id"] == "user_a"


def test_foreign_tailored_resume_is_invisible():
    application = create_app()
    application.dependency_overrides[get_current_user] = lambda: UserContext(subject="user_b")
    client = TestClient(application)
    tailored = TailoredResume(id="tailored-a")
    tailor.tailored_resumes[tailored.id] = tailored
    tailor.tailored_resume_owners[tailored.id] = "user_a"

    response = client.get("/api/v1/tailor/resume/tailored-a")

    assert response.status_code == 404
