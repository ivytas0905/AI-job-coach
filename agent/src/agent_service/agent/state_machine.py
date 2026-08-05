"""Deterministic state transitions for a tailoring run."""


class InvalidTransitionError(ValueError):
    pass


class WorkflowStateMachine:
    _transitions = {
        ("awaiting_resume", "resume_accepted"): "awaiting_jd",
        ("awaiting_jd", "jd_accepted"): "analyzing",
        ("analyzing", "proposal_created"): "proposal_ready",
        ("proposal_ready", "proposal_rejected"): "proposal_ready",
        ("proposal_ready", "revision_requested"): "proposal_ready",
        ("proposal_ready", "proposal_approved"): "applying",
        ("applying", "version_created"): "version_ready",
        ("version_ready", "export_requested"): "exporting",
        ("exporting", "export_created"): "completed",
        ("analyzing", "failed"): "failed",
        ("applying", "failed"): "failed",
        ("exporting", "failed"): "failed",
        ("failed", "retry_analysis"): "analyzing",
        ("failed", "retry_proposal"): "proposal_ready",
    }

    def transition(self, state: str, event: str) -> str:
        try:
            return self._transitions[(state, event)]
        except KeyError as exc:
            raise InvalidTransitionError(f"Event {event} is not allowed in state {state}") from exc
