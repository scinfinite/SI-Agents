from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.organization.models import AgentDefinition
from core.runtime.bridge import CallbackHarnessAdapter, adapter_metadata, is_harness_adapter
from core.runtime.deployment import HarnessDeploymentManifest, build_manifest
from core.runtime.engine import RuntimeEngine
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
from core.runtime.registry import HarnessRegistry
from core.runtime.wire import (
    WIRE_PROTOCOL,
    capabilities_to_dict,
    error_code,
    request_to_dict,
    response_status,
    response_to_dict,
    validate_wire_payload,
)
from core.teams.models import TaskDefinition, TeamDefinition


def test_callback_bridge_exposes_metadata_and_invokes() -> None:
    metadata = HarnessMetadata("test-harness", RuntimeKind.AGENT, "1.0")
    capabilities = RuntimeCapabilities(streaming=True, cancellation=True)
    cancelled: list[str] = []

    def invoke(request: InvocationRequest) -> InvocationResponse:
        return InvocationResponse(
            request.request_id,
            InvocationStatus.COMPLETED,
            output={"ok": True},
            events=(RuntimeEvent(RuntimeEventType.COMPLETED, request.request_id, 0),),
        )

    adapter = CallbackHarnessAdapter(
        metadata,
        capabilities,
        invoke,
        lambda request_id: cancelled.append(request_id) or True,
    )
    request = InvocationRequest("echo", "hello", "project")
    response = adapter.invoke(request)

    assert response.request_id == request.request_id
    assert is_harness_adapter(adapter)
    assert adapter.cancel(request.request_id) is True
    assert cancelled == [request.request_id]
    assert adapter_metadata(adapter)["harness"]["harness_id"] == "test-harness"


def test_callback_bridge_through_runtime_keeps_governance_boundary() -> None:
    metadata = HarnessMetadata("test-harness", RuntimeKind.AGENT, "1.0")

    def invoke(request: InvocationRequest) -> InvocationResponse:
        return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output="ok")

    adapter = CallbackHarnessAdapter(metadata, RuntimeCapabilities(), invoke)
    registry = HarnessRegistry()
    registry.register(adapter)
    registry.enable("test-harness")
    engine = RuntimeEngine(registry=registry)
    request = InvocationRequest(
        "echo",
        "hello",
        "project",
        governance=GovernanceRequest("runtime.test", RiskLevel.LOW, DataClass.PUBLIC),
    )

    response = engine.invoke("test-harness", request)
    assert response.status is InvocationStatus.COMPLETED
    assert response.output == "ok"


def test_callback_bridge_requires_cancel_callback_when_capability_is_declared() -> None:
    metadata = HarnessMetadata("test-harness", RuntimeKind.CLI, "1.0")
    try:
        CallbackHarnessAdapter(
            metadata,
            RuntimeCapabilities(cancellation=True),
            lambda request: InvocationResponse(request.request_id, InvocationStatus.CANCELLED),
        )
    except ValueError as exc:
        assert "cancel_callback" in str(exc)
    else:
        raise AssertionError("expected cancellation callback validation")


def test_wire_request_has_stable_protocol_envelope() -> None:
    request = InvocationRequest("echo", {"value": 1}, "project", metadata=(("source", "test"),))
    payload = request_to_dict(request)
    assert payload["protocol"] == WIRE_PROTOCOL
    assert payload["request_id"] == request.request_id
    assert payload["metadata"] == {"source": "test"}
    assert validate_wire_payload(payload) is payload


def test_wire_helpers_reject_unknown_protocol_and_parse_enums() -> None:
    response = InvocationResponse(
        "req-1",
        InvocationStatus.FAILED,
        error=RuntimeError(RuntimeErrorCode.TIMEOUT, "timed out"),
    )
    payload = response_to_dict(response)

    assert response_status(payload) is InvocationStatus.FAILED
    assert error_code(payload["error"]) is RuntimeErrorCode.TIMEOUT
    try:
        validate_wire_payload({"protocol": "si.runtime.v0"})
    except ValueError as exc:
        assert "protocol" in str(exc)
    else:
        raise AssertionError("expected protocol rejection")


def test_wire_rejects_non_json_values() -> None:
    request = InvocationRequest("echo", {"bad": object()}, "project")
    try:
        request_to_dict(request)
    except ValueError as exc:
        assert "JSON-compatible" in str(exc)
    else:
        raise AssertionError("expected JSON compatibility validation")


def test_capability_serialization_is_complete() -> None:
    capabilities = RuntimeCapabilities(True, True, True, True, True)
    assert capabilities_to_dict(capabilities) == {
        "streaming": True,
        "cancellation": True,
        "tool_calls": True,
        "structured_output": True,
        "session_continuity": True,
    }


def test_deployment_manifest_is_deterministic_and_non_authorizing() -> None:
    agent = AgentDefinition(
        id="developer",
        name="Developer",
        division="engineering",
        description="repair code",
        responsibilities=("repair",),
        deliverables=("change",),
        success_criteria=("tests",),
        boundaries=("no unverified claims",),
        skills=("verify-change",),
        capabilities=("code-edit",),
        permissions=("workspace_write",),
    )
    task = TaskDefinition(id="repair", agent_id="developer")
    team = TeamDefinition(
        id="repair-team",
        name="Repair Team",
        description="repair",
        members=("developer",),
        tasks=(task,),
        max_parallelism=1,
    )
    manifest = build_manifest(
        "test-harness",
        (agent,),
        (team,),
        skills=("verify-change",),
        capabilities=("streaming",),
    )
    assert manifest.as_dict() == {
        "protocol": "si.runtime.v1",
        "harness_id": "test-harness",
        "agents": ["developer"],
        "teams": ["repair-team"],
        "skills": ["verify-change"],
        "required_permissions": ["workspace_write"],
        "capabilities": ["streaming"],
    }


def test_manifest_rejects_duplicate_entries() -> None:
    try:
        HarnessDeploymentManifest("si.runtime.v1", "h", ("a", "a"), (), (), (), ())
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("expected duplicate rejection")
