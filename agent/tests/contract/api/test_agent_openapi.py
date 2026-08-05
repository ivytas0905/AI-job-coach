from agent_service.main import create_app


def test_agent_openapi_exposes_one_run_scoped_browser_contract():
    schema = create_app().openapi()
    paths = {path for path in schema["paths"] if path.startswith("/api/v1/agent")}

    assert paths == {
        "/api/v1/agent/runs",
        "/api/v1/agent/runs/{run_id}",
        "/api/v1/agent/runs/{run_id}/resume",
        "/api/v1/agent/runs/{run_id}/job-description",
        "/api/v1/agent/runs/{run_id}/messages",
        "/api/v1/agent/runs/{run_id}/evidence",
        "/api/v1/agent/runs/{run_id}/proposals/{proposal_id}/decisions",
        "/api/v1/agent/runs/{run_id}/versions/{version_id}",
        "/api/v1/agent/runs/{run_id}/versions/{version_id}/restore",
        "/api/v1/agent/runs/{run_id}/versions/{version_id}/exports",
        "/api/v1/agent/runs/{run_id}/exports/{export_id}/download",
        "/api/v1/agent/runs/{run_id}/events",
    }
    assert not any("/api/v1/api/" in path for path in schema["paths"])


def test_agent_mutation_contracts_require_revision_or_idempotency():
    schema = create_app().openapi()
    components = schema["components"]["schemas"]

    decision_required = set(components["ProposalDecisionRequest"]["required"])
    restore_required = set(components["RestoreVersionRequest"]["required"])
    export_required = set(components["CreateExportRequest"]["required"])

    assert {"decision", "expected_revision", "idempotency_key"} <= decision_required
    assert restore_required == {"idempotency_key"}
    assert {"format", "idempotency_key"} == export_required
