"""Deterministic reference harness used for conformance and local execution."""

from core.governance.engine import GovernanceEngine
from core.governance.models import DecisionStatus
from core.runtime.adapter import validate_capability_request
from core.runtime.models import (
    InvocationRequest, InvocationResponse, InvocationStatus, RuntimeCapabilities,
    RuntimeError, RuntimeErrorCode, RuntimeEvent, RuntimeEventType, RuntimeKind,
)
from core.runtime.protocol import HarnessMetadata


class LocalHarnessAdapter:
    """Reference adapter. It only invokes a caller-supplied capability function."""

    def __init__(self, capabilities: dict[str, callable], *, harness_id: str = "local") -> None:
        self._capabilities = dict(capabilities)
        self._metadata = HarnessMetadata(harness_id, RuntimeKind.EMBEDDED, "1")
        self._runtime_capabilities = RuntimeCapabilities(
            streaming=True, cancellation=True, tool_calls=False,
            structured_output=True, session_continuity=True,
        )
        self._cancelled: set[str] = set()
        self._governance = GovernanceEngine()

    @property
    def metadata(self) -> HarnessMetadata:
        return self._metadata

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return self._runtime_capabilities

    def invoke(self, request: InvocationRequest) -> InvocationResponse:
        unsupported = validate_capability_request(self, request)
        if unsupported:
            return InvocationResponse(request.request_id, InvocationStatus.FAILED, error=unsupported)
        if request.capability_id not in self._capabilities:
            return InvocationResponse(
                request.request_id, InvocationStatus.FAILED,
                error=RuntimeError(RuntimeErrorCode.NOT_SUPPORTED, "capability is not registered"),
            )
        if request.governance is None:
            return InvocationResponse(
                request.request_id, InvocationStatus.FAILED,
                error=RuntimeError(RuntimeErrorCode.GOVERNANCE_DENIED, "governance request is required"),
            )
        decision = self._governance.decide(request.governance)
        if decision.status != DecisionStatus.ALLOW:
            return InvocationResponse(
                request.request_id, InvocationStatus.FAILED,
                error=RuntimeError(RuntimeErrorCode.GOVERNANCE_DENIED, "governance did not allow invocation"),
            )
        if request.request_id in self._cancelled:
            return InvocationResponse(
                request.request_id, InvocationStatus.CANCELLED,
                events=(RuntimeEvent(RuntimeEventType.CANCELLED, request.request_id, 0),),
            )
        try:
            output = self._capabilities[request.capability_id](request.input)
        except Exception as exc:  # adapter boundary: normalize implementation failures
            return InvocationResponse(
                request.request_id, InvocationStatus.FAILED,
                error=RuntimeError(RuntimeErrorCode.EXECUTION_FAILED, str(exc) or "capability failed"),
            )
        event = RuntimeEvent(RuntimeEventType.COMPLETED, request.request_id, 0, output)
        return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output, (event,))

    def cancel(self, request_id: str) -> bool:
        self._cancelled.add(request_id)
        return True
