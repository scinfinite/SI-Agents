"""Transport-neutral adapter conformance checks."""

from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.runtime.adapter import validate_response
from core.runtime.models import InvocationRequest, InvocationStatus
from core.runtime.protocol import HarnessAdapter


class ConformanceFailure(AssertionError):
    """Raised when an adapter violates the runtime contract."""


def run_conformance(adapter: HarnessAdapter, capability_id: str = "echo") -> tuple[str, ...]:
    """Exercise correlation, terminal-state, response, and cancellation guarantees."""
    checks: list[str] = []
    request = InvocationRequest(
        capability_id=capability_id,
        input="conformance",
        project_id="conformance-project",
        governance=GovernanceRequest("runtime.conformance", RiskLevel.LOW, DataClass.PUBLIC),
    )
    response = adapter.invoke(request)
    if response.request_id != request.request_id:
        raise ConformanceFailure("response correlation failed")
    checks.append("correlation")
    if response.status not in {
        InvocationStatus.COMPLETED,
        InvocationStatus.FAILED,
        InvocationStatus.CANCELLED,
    }:
        raise ConformanceFailure("invalid terminal status")
    checks.append("terminal-status")
    try:
        validate_response(request, response)
    except ValueError as exc:
        raise ConformanceFailure(str(exc)) from exc
    checks.append("response-shape")
    if adapter.capabilities.cancellation:
        if adapter.cancel(request.request_id) is not True:
            raise ConformanceFailure("cancellation contract failed")
        checks.append("cancellation")
    return tuple(checks)
