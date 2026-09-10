"""Governed runtime coordinator for cross-harness invocation."""

from core.governance.engine import GovernanceEngine
from core.governance.models import DecisionStatus
from core.runtime.adapter import validate_capability_request, validate_response
from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeError,
    RuntimeErrorCode,
    RuntimeEvent,
    RuntimeEventType,
)
from core.runtime.registry import HarnessRegistry
from core.runtime.session import SessionRegistry


class RuntimeEngine:
    """Route invocations through an enabled harness without bypassing governance."""

    def __init__(
        self,
        registry: HarnessRegistry | None = None,
        sessions: SessionRegistry | None = None,
        governance: GovernanceEngine | None = None,
    ) -> None:
        self.registry = registry or HarnessRegistry()
        self.sessions = sessions or SessionRegistry()
        self.governance = governance or GovernanceEngine()

    def invoke(self, harness_id: str, request: InvocationRequest) -> InvocationResponse:
        """Validate isolation/policy, invoke the adapter, then normalize its response."""
        try:
            adapter = self.registry.get(harness_id)
        except KeyError:
            return self._failure(request, RuntimeErrorCode.NOT_SUPPORTED, "harness is not registered")
        except PermissionError:
            return self._failure(request, RuntimeErrorCode.NOT_SUPPORTED, "harness is not enabled")

        if request.session_id is not None:
            try:
                self.sessions.require(
                    request.session_id,
                    project_id=request.project_id,
                    harness_id=harness_id,
                )
            except KeyError:
                return self._failure(request, RuntimeErrorCode.SESSION_NOT_FOUND, "session not found")
            except (PermissionError, ValueError) as exc:
                return self._failure(request, RuntimeErrorCode.INVALID_REQUEST, str(exc))

        capability_error = validate_capability_request(adapter, request)
        if capability_error is not None:
            return self._failure(request, capability_error.code, capability_error.message)

        if request.governance is None:
            return self._failure(request, RuntimeErrorCode.GOVERNANCE_DENIED, "governance request is required")
        decision = self.governance.decide(request.governance)
        if decision.status is not DecisionStatus.ALLOW:
            return self._failure(
                request,
                RuntimeErrorCode.GOVERNANCE_DENIED,
                "; ".join(decision.reasons) or "governance did not allow invocation",
            )

        try:
            response = adapter.invoke(request)
        except Exception:  # noqa: BLE001 - adapter boundary must normalize arbitrary implementations
            return self._failure(request, RuntimeErrorCode.EXECUTION_FAILED, "harness invocation failed")
        try:
            validate_response(request, response)
        except ValueError as exc:
            return self._failure(request, RuntimeErrorCode.EXECUTION_FAILED, str(exc))
        return response

    def cancel(self, harness_id: str, request_id: str) -> bool:
        """Forward cancellation only to an explicitly enabled harness."""
        if not request_id.strip():
            return False
        return self.registry.get(harness_id).cancel(request_id)

    @staticmethod
    def _failure(
        request: InvocationRequest,
        code: RuntimeErrorCode,
        message: str,
    ) -> InvocationResponse:
        event_type = RuntimeEventType.CANCELLED if code is RuntimeErrorCode.CANCELLED else RuntimeEventType.FAILED
        status = InvocationStatus.CANCELLED if code is RuntimeErrorCode.CANCELLED else InvocationStatus.FAILED
        return InvocationResponse(
            request.request_id,
            status,
            events=(RuntimeEvent(event_type, request.request_id, 0),),
            error=None if status is InvocationStatus.CANCELLED else RuntimeError(code, message or code.value),
        )
