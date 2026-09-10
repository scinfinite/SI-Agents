"""Deterministic reference harness used for conformance and local execution."""

from collections.abc import Callable
from time import monotonic

from core.governance.engine import GovernanceEngine
from core.governance.models import DecisionStatus
from core.runtime.adapter import validate_capability_request
from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeCapabilities,
    RuntimeError,
    RuntimeErrorCode,
    RuntimeEvent,
    RuntimeEventType,
    RuntimeKind,
)
from core.runtime.protocol import HarnessMetadata


class LocalHarnessAdapter:
    """Reference adapter that invokes caller-supplied functions without external I/O."""

    def __init__(
        self,
        capabilities: dict[str, Callable[[object], object]],
        *,
        harness_id: str = "local",
        version: str = "1",
    ) -> None:
        self._capabilities = dict(capabilities)
        self._metadata = HarnessMetadata(harness_id, RuntimeKind.EMBEDDED, version)
        self._runtime_capabilities = RuntimeCapabilities(
            streaming=True,
            cancellation=True,
            tool_calls=False,
            structured_output=True,
            session_continuity=True,
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
        if request.governance is None:
            return self._denied(request, "governance request is required")
        decision = self._governance.decide(request.governance)
        if decision.status is not DecisionStatus.ALLOW:
            return self._denied(request, "; ".join(decision.reasons) or "governance did not allow invocation")
        if request.capability_id not in self._capabilities:
            return InvocationResponse(
                request.request_id,
                InvocationStatus.FAILED,
                error=RuntimeError(RuntimeErrorCode.NOT_SUPPORTED, "capability is not registered"),
            )
        if request.request_id in self._cancelled:
            return InvocationResponse(
                request.request_id,
                InvocationStatus.CANCELLED,
                events=(RuntimeEvent(RuntimeEventType.CANCELLED, request.request_id, 0),),
            )

        started = monotonic()
        try:
            output = self._capabilities[request.capability_id](request.input)
        except Exception as exc:  # adapter boundary: normalize implementation failures
            return InvocationResponse(
                request.request_id,
                InvocationStatus.FAILED,
                error=RuntimeError(RuntimeErrorCode.EXECUTION_FAILED, str(exc) or "capability failed"),
            )
        if request.timeout_seconds is not None and monotonic() - started > request.timeout_seconds:
            return InvocationResponse(
                request.request_id,
                InvocationStatus.FAILED,
                error=RuntimeError(RuntimeErrorCode.TIMEOUT, "capability exceeded its cooperative timeout", True),
            )
        if request.request_id in self._cancelled:
            return InvocationResponse(
                request.request_id,
                InvocationStatus.CANCELLED,
                events=(RuntimeEvent(RuntimeEventType.CANCELLED, request.request_id, 0),),
            )

        if request.streaming:
            events = (
                RuntimeEvent(RuntimeEventType.STARTED, request.request_id, 0),
                RuntimeEvent(RuntimeEventType.DELTA, request.request_id, 1, output),
                RuntimeEvent(RuntimeEventType.COMPLETED, request.request_id, 2, output),
            )
        else:
            events = (RuntimeEvent(RuntimeEventType.COMPLETED, request.request_id, 0, output),)
        return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output, events)

    def cancel(self, request_id: str) -> bool:
        if not request_id.strip():
            return False
        self._cancelled.add(request_id)
        return True

    @staticmethod
    def _denied(request: InvocationRequest, message: str) -> InvocationResponse:
        return InvocationResponse(
            request.request_id,
            InvocationStatus.FAILED,
            error=RuntimeError(RuntimeErrorCode.GOVERNANCE_DENIED, message),
        )
