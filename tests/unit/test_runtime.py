from dataclasses import replace
from time import sleep

import pytest

from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.runtime import (
    HarnessMetadata,
    HarnessRegistry,
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    LocalHarnessAdapter,
    RuntimeCapabilities,
    RuntimeEngine,
    RuntimeErrorCode,
    RuntimeEvent,
    RuntimeEventType,
    RuntimeKind,
    RuntimeSession,
    SessionRegistry,
    run_conformance,
)
from core.runtime.adapter import validate_response
from core.runtime.protocol import HarnessAdapter, normalize_metadata


def governance() -> GovernanceRequest:
    return GovernanceRequest("test.invoke", RiskLevel.LOW, DataClass.PUBLIC)


def test_local_adapter_invokes_and_correlates() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    request = InvocationRequest("echo", "hello", "project", governance=governance())
    response = adapter.invoke(request)
    assert response.status == InvocationStatus.COMPLETED
    assert response.output == "hello"
    validate_response(request, response)


def test_governance_is_required_and_denials_fail_closed() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    request = InvocationRequest("echo", "x", "project")
    assert adapter.invoke(request).error.code.value == "governance_denied"
    denied = replace(governance(), destructive=True, production=True, risk=RiskLevel.HIGH)
    request = replace(request, governance=denied)
    assert adapter.invoke(request).error.code.value == "governance_denied"


def test_unknown_capability_is_normalized() -> None:
    adapter = LocalHarnessAdapter({})
    request = InvocationRequest("missing", None, "project", governance=governance())
    response = adapter.invoke(request)
    assert response.status == InvocationStatus.FAILED
    assert response.error.code.value == "not_supported"


def test_streaming_has_start_delta_and_terminal_events() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    request = InvocationRequest("echo", "x", "project", governance=governance(), streaming=True)
    response = adapter.invoke(request)
    assert response.status == InvocationStatus.COMPLETED
    assert [event.type for event in response.events] == [
        RuntimeEventType.STARTED,
        RuntimeEventType.DELTA,
        RuntimeEventType.COMPLETED,
    ]
    validate_response(request, response)


def test_registry_is_disabled_by_default_and_duplicate_safe() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    registry = HarnessRegistry()
    registry.register(adapter)
    with pytest.raises(PermissionError):
        registry.get("local")
    registry.enable("local")
    assert registry.get("local") is adapter
    with pytest.raises(ValueError):
        registry.register(adapter)
    registry.disable("local")
    with pytest.raises(PermissionError):
        registry.get("local")


def test_sessions_preserve_project_and_harness_isolation() -> None:
    registry = SessionRegistry()
    session = RuntimeSession("s1", "project-a", "local")
    registry.create(session)
    assert registry.require("s1", project_id="project-a", harness_id="local") == session
    with pytest.raises(PermissionError):
        registry.require("s1", project_id="project-b", harness_id="local")
    assert registry.close("s1").status.value == "closed"
    assert registry.close("s1").status.value == "closed"
    with pytest.raises(ValueError):
        registry.create(session)
    with pytest.raises(ValueError):
        registry.require("s1", project_id="project-a", harness_id="local")


def test_metadata_is_deterministically_normalized() -> None:
    assert normalize_metadata({"z": 2, "a": True}) == (("a", "True"), ("z", "2"))
    assert HarnessMetadata("cli", RuntimeKind.CLI, "1").harness_id == "cli"


def test_conformance_suite() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    assert run_conformance(adapter) == ("correlation", "terminal-status", "response-shape", "cancellation")


def test_runtime_engine_requires_enabled_harness() -> None:
    engine = RuntimeEngine()
    request = InvocationRequest("echo", "x", "project", governance=governance())
    response = engine.invoke("local", request)
    assert response.error.code.value == "not_supported"


def test_runtime_engine_enforces_governance_before_adapter() -> None:
    registry = HarnessRegistry()
    adapter = LocalHarnessAdapter({"echo": lambda value: pytest.fail("must not execute")})
    registry.register(adapter, enabled=True)
    engine = RuntimeEngine(registry=registry)
    request = InvocationRequest("echo", "x", "project")
    response = engine.invoke("local", request)
    assert response.error.code.value == "governance_denied"


def test_runtime_engine_enforces_session_isolation() -> None:
    registry = HarnessRegistry()
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    registry.register(adapter, enabled=True)
    sessions = SessionRegistry()
    sessions.create(RuntimeSession("s1", "project-a", "local"))
    engine = RuntimeEngine(registry=registry, sessions=sessions)
    request = InvocationRequest("echo", "x", "project-b", session_id="s1", governance=governance())
    response = engine.invoke("local", request)
    assert response.error.code.value == "invalid_request"


def test_runtime_engine_rejects_closed_session() -> None:
    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": lambda value: value}), enabled=True)
    sessions = SessionRegistry()
    sessions.create(RuntimeSession("s1", "project", "local"))
    sessions.close("s1")
    response = RuntimeEngine(registry=registry, sessions=sessions).invoke(
        "local",
        InvocationRequest("echo", "x", "project", session_id="s1", governance=governance()),
    )
    assert response.error.code.value == "invalid_request"


def test_runtime_engine_normalizes_adapter_exception_without_leaking_details() -> None:
    class ExplodingAdapter:
        metadata = HarnessMetadata("explode", RuntimeKind.AGENT, "1")
        capabilities = RuntimeCapabilities()

        def invoke(self, request: InvocationRequest) -> InvocationResponse:
            raise RuntimeError("secret-detail")

        def cancel(self, request_id: str) -> bool:
            return True

    registry = HarnessRegistry()
    registry.register(ExplodingAdapter(), enabled=True)
    response = RuntimeEngine(registry=registry).invoke(
        "explode",
        InvocationRequest("echo", "x", "project", governance=governance()),
    )
    assert response.error.code.value == "execution_failed"
    assert response.error.message == "harness invocation failed"
    assert "secret-detail" not in response.error.message


def test_runtime_engine_rejects_malformed_response() -> None:
    class BadAdapter:
        metadata = HarnessMetadata("bad", RuntimeKind.API, "1")
        capabilities = RuntimeCapabilities()

        def invoke(self, request: InvocationRequest) -> InvocationResponse:
            return InvocationResponse("wrong-request", InvocationStatus.COMPLETED, output="bad")

        def cancel(self, request_id: str) -> bool:
            return True

    registry = HarnessRegistry()
    registry.register(BadAdapter(), enabled=True)
    response = RuntimeEngine(registry=registry).invoke(
        "bad",
        InvocationRequest("echo", "x", "project", governance=governance()),
    )
    assert response.error.code.value == "execution_failed"
    assert "request_id mismatch" in response.error.message


def test_runtime_engine_cancel_is_forwarded_and_prevents_local_execution() -> None:
    called = False

    def handler(value: object) -> object:
        nonlocal called
        called = True
        return value

    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": handler}), enabled=True)
    engine = RuntimeEngine(registry=registry)
    request = InvocationRequest("echo", "x", "project", governance=governance())
    assert engine.cancel("local", request.request_id) is True
    response = engine.invoke("local", request)
    assert response.status == InvocationStatus.CANCELLED
    assert response.events[0].type is RuntimeEventType.CANCELLED
    assert not called


def test_local_adapter_timeout_is_cooperative() -> None:
    def slow(_: object) -> object:
        sleep(0.01)
        return "late"

    adapter = LocalHarnessAdapter({"slow": slow})
    request = InvocationRequest("slow", None, "project", governance=governance(), timeout_seconds=0.001)
    response = adapter.invoke(request)
    assert response.error.code is RuntimeErrorCode.TIMEOUT
    assert response.error.retryable is True


def test_capability_request_rejects_streaming_when_unsupported() -> None:
    class NonStreamingAdapter:
        metadata = HarnessMetadata("plain", RuntimeKind.CLI, "1")
        capabilities = RuntimeCapabilities()

        def invoke(self, request: InvocationRequest) -> InvocationResponse:
            return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output="x")

        def cancel(self, request_id: str) -> bool:
            return False

    registry = HarnessRegistry()
    registry.register(NonStreamingAdapter(), enabled=True)
    response = RuntimeEngine(registry=registry).invoke(
        "plain",
        InvocationRequest("echo", "x", "project", governance=governance(), streaming=True),
    )
    assert response.error.code.value == "not_supported"


def test_runtime_protocol_is_runtime_checkable() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    assert isinstance(adapter, HarnessAdapter)


def test_request_and_response_reject_duplicate_metadata_or_usage() -> None:
    with pytest.raises(ValueError):
        InvocationRequest("echo", "x", "project", metadata=(("a", "1"), ("a", "2")))
    with pytest.raises(ValueError):
        InvocationResponse("r", InvocationStatus.COMPLETED, usage=(("tokens", 1), ("tokens", 2)))


def test_event_and_usage_validation_is_fail_closed() -> None:
    with pytest.raises(ValueError):
        RuntimeEvent(RuntimeEventType.STARTED, "r", -1)
    with pytest.raises(ValueError):
        InvocationResponse("r", InvocationStatus.COMPLETED, usage=(("tokens", -1),))
