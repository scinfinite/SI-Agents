"""Adapter validation and transport-neutral invocation helpers."""

from core.runtime.models import InvocationRequest, InvocationResponse, RuntimeError, RuntimeErrorCode
from core.runtime.protocol import HarnessAdapter


def validate_capability_request(adapter: HarnessAdapter, request: InvocationRequest) -> RuntimeError | None:
    caps = adapter.capabilities
    if request.streaming and not caps.streaming:
        return RuntimeError(RuntimeErrorCode.NOT_SUPPORTED, "streaming is not supported")
    return None


def validate_response(request: InvocationRequest, response: InvocationResponse) -> None:
    if response.request_id != request.request_id:
        raise ValueError("adapter response request_id mismatch")
    if request.streaming and not response.events and response.error is None:
        raise ValueError("streaming invocation must return normalized events")
