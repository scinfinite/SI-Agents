"""Language-neutral serialization for the SI runtime protocol.

The wire contract deliberately uses JSON-compatible primitives so adapters in
other languages do not need Python implementation details.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeCapabilities,
    RuntimeError,
    RuntimeErrorCode,
    RuntimeEvent,
    RuntimeEventType,
)
from core.runtime.protocol import HarnessMetadata

WIRE_PROTOCOL = "si.runtime.v1"


def _enum(value: Enum) -> str:
    return value.value


def _timestamp(value: datetime) -> str:
    return value.isoformat()


def capabilities_to_dict(value: RuntimeCapabilities) -> dict[str, bool]:
    return {
        "streaming": value.streaming,
        "cancellation": value.cancellation,
        "tool_calls": value.tool_calls,
        "structured_output": value.structured_output,
        "session_continuity": value.session_continuity,
    }


def metadata_to_dict(value: HarnessMetadata) -> dict[str, str]:
    return {"harness_id": value.harness_id, "kind": value.kind.value, "version": value.version}


def event_to_dict(value: RuntimeEvent) -> dict[str, Any]:
    return {
        "type": _enum(value.type),
        "request_id": value.request_id,
        "sequence": value.sequence,
        "data": value.data,
        "emitted_at": _timestamp(value.emitted_at),
    }


def error_to_dict(value: RuntimeError) -> dict[str, Any]:
    return {"code": _enum(value.code), "message": value.message, "retryable": value.retryable}


def request_to_dict(value: InvocationRequest) -> dict[str, Any]:
    return {
        "protocol": WIRE_PROTOCOL,
        "request_id": value.request_id,
        "capability_id": value.capability_id,
        "input": value.input,
        "project_id": value.project_id,
        "session_id": value.session_id,
        "metadata": dict(value.metadata),
        "governance": value.governance,
        "timeout_seconds": value.timeout_seconds,
        "streaming": value.streaming,
    }


def response_to_dict(value: InvocationResponse) -> dict[str, Any]:
    return {
        "protocol": WIRE_PROTOCOL,
        "request_id": value.request_id,
        "status": _enum(value.status),
        "output": value.output,
        "events": [event_to_dict(event) for event in value.events],
        "error": error_to_dict(value.error) if value.error else None,
        "usage": dict(value.usage),
    }


def _require_protocol(payload: dict[str, Any]) -> None:
    if payload.get("protocol") != WIRE_PROTOCOL:
        raise ValueError("unsupported or missing runtime wire protocol")


def validate_wire_payload(payload: object) -> dict[str, Any]:
    """Validate only the envelope shape; domain validation remains in models."""
    if not isinstance(payload, dict):
        raise ValueError("wire payload must be an object")
    _require_protocol(payload)
    return payload


def response_status(payload: dict[str, Any]) -> InvocationStatus:
    """Parse a response status without constructing an untrusted response."""
    validate_wire_payload(payload)
    try:
        return InvocationStatus(str(payload["status"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid response status") from exc


def error_code(payload: dict[str, Any]) -> RuntimeErrorCode:
    """Parse an error code from a normalized error object."""
    if not isinstance(payload, dict):
        raise ValueError("error payload must be an object")
    try:
        return RuntimeErrorCode(str(payload["code"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid runtime error code") from exc
