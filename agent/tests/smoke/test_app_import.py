from agent_service.main import create_app


def test_application_imports_and_registers_required_routes():
    app = create_app()
    paths = set(app.openapi()["paths"])

    assert "/health" in paths
    assert any(path.startswith("/api/v1") for path in paths)
