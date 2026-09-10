from dataclasses import replace

import pytest

from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.runtime import (
    HarnessRegistry, InvocationRequest, InvocationStatus, LocalHarnessAdapter,
    RuntimeSession, SessionRegistry, run_conformance,
)
from core.runtime.adapter import validate_response
from core.runtime.protocol import HarnessMetadata, normalize_metadata
from core.runtime.models import RuntimeKind


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
    denied = replace(governance(), destructive=True, production=True)
    request = replace(request, governance=denied)
    assert adapter.invoke(request).error.code.value == "governance_denied"


def test_unknown_capability_is_normalized() -> None:
    adapter = LocalHarnessAdapter({})
    request = InvocationRequest("missing", None, "project", governance=governance())
    response = adapter.invoke(request)
    assert response.status == InvocationStatus.FAILED
    assert response.error.code.value == "not_supported"


def test_streaming_capability_and_event_contract() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    request = InvocationRequest("echo", "x", "project", governance=governance(), streaming=True)
    response = adapter.invoke(request)
    assert response.status == InvocationStatus.COMPLETED
    assert response.events[0].request_id == request.request_id
    assert response.events[0].sequence == 0


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


def test_sessions_preserve_project_isolation() -> None:
    registry = SessionRegistry()
    session = RuntimeSession("s1", "project-a", "local")
    registry.create(session)
    assert registry.get("s1").project_id == "project-a"
    assert registry.close("s1").status.value == "closed"
    with pytest.raises(ValueError):
        registry.create(session)


def test_metadata_is_deterministically_normalized() -> None:
    assert normalize_metadata({"z": 2, "a": True}) == (("a", "True"), ("z", "2"))
    assert HarnessMetadata("cli", RuntimeKind.CLI, "1").harness_id == "cli"


def test_conformance_suite() -> None:
    adapter = LocalHarnessAdapter({"echo": lambda value: value})
    assert run_conformance(adapter) == ("correlation", "terminal-status", "cancellation")


def test_invalid_timeout_fails_closed() -> None:
    with pytest.raises(ValueError):
        InvocationRequest("echo", "x", "project", timeout_seconds=0)
