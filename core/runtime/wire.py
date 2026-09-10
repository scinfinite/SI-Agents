"""Language-neutral serialization for the SI runtime protocol."""

from datetime import datetime
from enum import Enum
from typing import Any

from core.governance.models import GovernanceRequest
from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeCapabilities,
    RuntimeError,
    RuntimeErrorCode,
    RuntimeEvent,
)
from core.runtime.protocol import HarnessMetadata

WIRE_PROTOCOL = "si.runtime.v1"


def _enum(value: Enum) -> str:
    return value.value


def _timestamp(value: datetime) -> str:
    return value.isoformat()


def capabilities_to_dict(value: RuntimeCapabilities) -> dict[str, bool]:
    return {"streaming": value.streaming, "cancellation": value.cancellation, "tool_calls": value.tool_calls, "structured_output": value.structured_output, "session_continuity": value.session_continuity}


def metadata_to_dict(value: HarnessMetadata) -> dict[str, str]:
    return {"harness_id": value.harness_id, "kind": value.kind.value, "version": value.version}


def governance_to_dict(value: GovernanceRequest) -> dict[str, Any]:
    approval = None
    if value.approval is not None:
        approval = {"approved_by": value.approval.approved_by, "reason": value.approval.reason, "reference": value.approval.reference}
    return {"action": value.action, "risk": value.risk.value, "data_class": value.data_class.value, "external_egress": value.external_egress, "paid_resource": value.paid_resource, "destructive": value.destructive, "production": value.production, "credential": value.credential, "publication": value.publication, "legal_review_required": value.legal_review_required, "estimated_cost": value.estimated_cost, "approval": approval, "provenance": list(value.provenance)}


def event_to_dict(value: RuntimeEvent) -> dict[str, Any]:
    return {"type": _enum(value.type), "request_id": value.request_id, "sequence": value.sequence, "data": value.data, "emitted_at": _timestamp(value.emitted_at)}


def error_to_dict(value: RuntimeError) -> dict[str, Any]:
    return {"code": _enum(value.code), "message": value.message, "retryable": value.retryable}


def request_to_dict(value: InvocationRequest) -> dict[str, Any]:
    return {"protocol": WIRE_PROTOCOL, "request_id": value.request_id, "capability_id": value.capability_id, "input": value.input, "project_id": value.project_id, "session_id": value.session_id, "metadata": dict(value.metadata), "governance": governance_to_dict(value.governance) if value.governance else None, "timeout_seconds": value.timeout_seconds, "streaming": value.streaming}


def response_to_dict(value: InvocationResponse) -> dict[str, Any]:
    return {"protocol": WIRE_PROTOCOL, "request_id": value.request_id, "status": _enum(value.status), "output": value.output, "events": [event_to_dict(event) for event in value.events], "error": error_to_dict(value.error) if value.error else None, "usage": dict(value.usage)}


def validate_wire_payload(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("wire payload must be an object")
    if payload.get("protocol") != WIRE_PROTOCOL:
        raise ValueError("unsupported or missing runtime wire protocol")
    return payload


def response_status(payload: dict[str, Any]) -> InvocationStatus:
    validate_wire_payload(payload)
    try:
        return InvocationStatus(str(payload["status"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid response status") from exc


def error_code(payload: dict[str, Any]) -> RuntimeErrorCode:
    if not isinstance(payload, dict):
        raise ValueError("error payload must be an object")
    try:
        return RuntimeErrorCode(str(payload["code"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid runtime error code") from exc
