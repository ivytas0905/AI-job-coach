import pytest

from agent_service.agent.state_machine import InvalidTransitionError, WorkflowStateMachine


def test_state_machine_allows_ordered_resume_to_proposal_flow():
    machine = WorkflowStateMachine()

    assert machine.transition("awaiting_resume", "resume_accepted") == "awaiting_jd"
    assert machine.transition("awaiting_jd", "jd_accepted") == "analyzing"
    assert machine.transition("analyzing", "proposal_created") == "proposal_ready"


def test_state_machine_only_allows_approval_to_apply():
    machine = WorkflowStateMachine()

    with pytest.raises(InvalidTransitionError):
        machine.transition("proposal_ready", "export_requested")

    assert machine.transition("proposal_ready", "proposal_approved") == "applying"


def test_failed_workflow_retries_from_last_safe_state():
    machine = WorkflowStateMachine()

    assert machine.transition("analyzing", "failed") == "failed"
    assert machine.transition("failed", "retry_analysis") == "analyzing"
