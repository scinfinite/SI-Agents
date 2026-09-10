"""Adapter validation and transport-neutral invocation helpers."""

from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeError,
    RuntimeErrorCode,
    RuntimeEventType,
)
from core.runtime.protocol import HarnessAdapter


def validate_capability_request(adapter: HarnessAdapter, request: InvocationRequest) -> RuntimeError | None:
    """Return a normalized error when the requested runtime feature is unsupported."""
    caps = adapter.capabilities
    if request.streaming and not caps.streaming:
        return RuntimeError(RuntimeErrorCode.NOT_SUPPORTED, "streaming is not supported")
    return None


def validate_response(request: InvocationRequest, response: InvocationResponse) -> None:
    """Reject malformed adapter output before it crosses the runtime boundary."""
    if response.request_id != request.request_id:
        raise ValueError("adapter response request_id mismatch")
    if response.status is InvocationStatus.FAILED and response.error is None:
        raise ValueError("failed response must contain an error")
    if response.status is not InvocationStatus.FAILED and response.error is not None:
        raise ValueError("non-failed response must not contain an error")
    sequences = [event.sequence for event in response.events]
    if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
        raise ValueError("response events must have unique ordered sequences")
    if any(event.request_id != request.request_id for event in response.events):
        raise ValueError("response event request_id mismatch")
    if request.streaming:
        if not response.events:
            raise ValueError("streaming invocation must return normalized events")
        if response.events[-1].type not in {
            RuntimeEventType.COMPLETED,
            RuntimeEventType.FAILED,
            RuntimeEventType.CANCELLED,
        }:
            raise ValueError("streaming response must terminate with a terminal event")
