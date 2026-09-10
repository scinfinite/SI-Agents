"""Universal callback bridge for harness-specific adapters.

Harness integrations own transport and lifecycle details. This bridge owns the
stable SI contract and keeps arbitrary callbacks behind one normalization point.
"""

from collections.abc import Callable
from typing import Any

from core.runtime.models import InvocationRequest, InvocationResponse, RuntimeCapabilities
from core.runtime.protocol import HarnessAdapter, HarnessMetadata

InvokeCallback = Callable[[InvocationRequest], InvocationResponse]
CancelCallback = Callable[[str], bool]


class CallbackHarnessAdapter:
    """Adapt an external harness callback pair to the SI HarnessAdapter contract."""

    def __init__(
        self,
        metadata: HarnessMetadata,
        capabilities: RuntimeCapabilities,
        invoke_callback: InvokeCallback,
        cancel_callback: CancelCallback | None = None,
    ) -> None:
        if not callable(invoke_callback):
            raise TypeError("invoke_callback must be callable")
        if capabilities.cancellation and cancel_callback is None:
            raise ValueError("cancellation capability requires cancel_callback")
        self._metadata = metadata
        self._capabilities = capabilities
        self._invoke_callback = invoke_callback
        self._cancel_callback = cancel_callback

    @property
    def metadata(self) -> HarnessMetadata:
        return self._metadata

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return self._capabilities

    def invoke(self, request: InvocationRequest) -> InvocationResponse:
        response = self._invoke_callback(request)
        if not isinstance(response, InvocationResponse):
            raise TypeError("harness callback must return InvocationResponse")
        return response

    def cancel(self, request_id: str) -> bool:
        if self._cancel_callback is None:
            return False
        return bool(self._cancel_callback(request_id))


def is_harness_adapter(value: object) -> bool:
    """Runtime-safe structural check used by adapter loaders and tests."""
    return isinstance(value, HarnessAdapter)


def adapter_metadata(value: HarnessAdapter) -> dict[str, Any]:
    """Return a transport-neutral descriptor suitable for discovery APIs."""
    return {
        "harness": {
            "harness_id": value.metadata.harness_id,
            "kind": value.metadata.kind.value,
            "version": value.metadata.version,
        },
        "capabilities": {
            "streaming": value.capabilities.streaming,
            "cancellation": value.capabilities.cancellation,
            "tool_calls": value.capabilities.tool_calls,
            "structured_output": value.capabilities.structured_output,
            "session_continuity": value.capabilities.session_continuity,
        },
    }
