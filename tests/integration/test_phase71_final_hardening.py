from threading import Barrier, Thread

import pytest

from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.runtime import (
    HarnessRegistry,
    InvocationLedger,
    InvocationRequest,
    InvocationStatus,
    LocalHarnessAdapter,
    RuntimeEngine,
)


def governance() -> GovernanceRequest:
    return GovernanceRequest("phase71.invoke", RiskLevel.LOW, DataClass.PUBLIC)


def test_duplicate_request_is_idempotent_and_executes_once() -> None:
    calls = 0

    def handler(value: object) -> object:
        nonlocal calls
        calls += 1
        return value

    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": handler}), enabled=True)
    engine = RuntimeEngine(registry=registry)
    request = InvocationRequest("echo", "stable", "project", request_id="req-1", governance=governance())

    first = engine.invoke("local", request)
    second = engine.invoke("local", request)

    assert first == second
    assert first.status is InvocationStatus.COMPLETED
    assert calls == 1


def test_request_id_cannot_be_reused_for_a_different_payload() -> None:
    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": lambda value: value}), enabled=True)
    engine = RuntimeEngine(registry=registry)
    first = InvocationRequest("echo", "one", "project", request_id="req-2", governance=governance())
    second = InvocationRequest("echo", "two", "project", request_id="req-2", governance=governance())

    assert engine.invoke("local", first).status is InvocationStatus.COMPLETED
    response = engine.invoke("local", second)
    assert response.status is InvocationStatus.FAILED
    assert response.error is not None
    assert response.error.code.value == "invalid_request"


def test_same_request_id_is_isolated_between_harnesses() -> None:
    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": lambda value: f"local:{value}"}), enabled=True)
    registry.register(LocalHarnessAdapter({"echo": lambda value: f"other:{value}"}, harness_id="other"), enabled=True)
    engine = RuntimeEngine(registry=registry)
    request = InvocationRequest("echo", "x", "project", request_id="req-3", governance=governance())

    local = engine.invoke("local", request)
    other = engine.invoke("other", request)

    assert local.output == "local:x"
    assert other.output == "other:x"


def test_cancel_is_terminal_and_replayed_without_execution() -> None:
    called = False

    def handler(value: object) -> object:
        nonlocal called
        called = True
        return value

    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": handler}), enabled=True)
    engine = RuntimeEngine(registry=registry)
    request = InvocationRequest("echo", "x", "project", request_id="req-4", governance=governance())

    assert engine.cancel("local", request.request_id) is True
    first = engine.invoke("local", request)
    second = engine.invoke("local", request)

    assert first.status is InvocationStatus.CANCELLED
    assert second == first
    assert not called


def test_ledger_is_bounded() -> None:
    ledger = InvocationLedger(max_entries=2)
    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": lambda value: value}), enabled=True)
    engine = RuntimeEngine(registry=registry, ledger=ledger)

    for index in range(3):
        request = InvocationRequest("echo", index, "project", request_id=f"req-{index}", governance=governance())
        assert engine.invoke("local", request).status is InvocationStatus.COMPLETED

    assert ledger.get("local", "req-0") is None
    assert ledger.get("local", "req-1") is not None
    assert ledger.get("local", "req-2") is not None


def test_concurrent_duplicate_requests_never_execute_twice() -> None:
    calls = 0
    barrier = Barrier(2)

    def handler(value: object) -> object:
        nonlocal calls
        calls += 1
        barrier.wait(timeout=2)
        return value

    registry = HarnessRegistry()
    registry.register(LocalHarnessAdapter({"echo": handler}), enabled=True)
    engine = RuntimeEngine(registry=registry)
    request = InvocationRequest("echo", "x", "project", request_id="req-5", governance=governance())
    responses: list[object] = []

    def invoke() -> None:
        responses.append(engine.invoke("local", request))

    first = Thread(target=invoke)
    second = Thread(target=invoke)
    first.start()
    second.start()
    first.join(timeout=3)
    second.join(timeout=3)

    assert len(responses) == 2
    assert calls == 1
    assert sorted(response.status.value for response in responses) == ["completed", "failed"]
    assert any(response.error and response.error.code.value == "invalid_request" for response in responses)


def test_ledger_rejects_invalid_capacity() -> None:
    with pytest.raises(ValueError):
        InvocationLedger(max_entries=0)
