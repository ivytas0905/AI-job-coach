from agent_service.domain.resume_policies import enforce_metric_evidence


def test_unsupported_metric_is_rejected_with_evidence_request():
    result = enforce_metric_evidence("Built a service", "Built a service serving 1,500 users")
    assert result.accepted_text == "Built a service"
    assert result.unsupported_metrics == ("1,500",)
    assert "source evidence" in result.evidence_request


def test_equivalent_supported_metric_is_allowed():
    result = enforce_metric_evidence("Processed 1,500 requests", "Processed 1500 requests")
    assert result.accepted_text == "Processed 1500 requests"
    assert result.evidence_request is None
