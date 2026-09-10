from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.runtime import (
    HarnessRegistry,
    InvocationRequest,
    InvocationStatus,
    LocalHarnessAdapter,
    RuntimeEngine,
    RuntimeEventType,
    RuntimeSession,
    SessionRegistry,
)


def test_runtime_engine_executes_a_governed_session_end_to_end() -> None:
    calls: list[object] = []

    def capability(value: object) -> object:
        calls.append(value)
        return {"echo": value}

    registry = HarnessRegistry()
    registry.register(
        LocalHarnessAdapter({"echo": capability}, harness_id="acceptance-local", version="1"),
        enabled=True,
    )
    sessions = SessionRegistry()
    sessions.create(RuntimeSession("session-1", "project-1", "acceptance-local"))
    engine = RuntimeEngine(registry=registry, sessions=sessions)

    request = InvocationRequest(
        "echo",
        "phase-19",
        "project-1",
        session_id="session-1",
        streaming=True,
        governance=GovernanceRequest("runtime.acceptance", RiskLevel.LOW, DataClass.PUBLIC),
    )
    response = engine.invoke("acceptance-local", request)

    assert response.status is InvocationStatus.COMPLETED
    assert response.output == {"echo": "phase-19"}
    assert calls == ["phase-19"]
    assert [event.type for event in response.events] == [
        RuntimeEventType.STARTED,
        RuntimeEventType.DELTA,
        RuntimeEventType.COMPLETED,
    ]
