from core.runtime.bridge import CallbackHarnessAdapter
from core.runtime.cross_runtime import CrossRuntimeGateway, HarnessHealth
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
from core.runtime.portable import PortableAdapterDescriptor, PortableAdapterKind, PortableAdapterRegistry
from core.runtime.protocol import HarnessMetadata
from core.runtime.registry import HarnessRegistry
from core.runtime.session import RuntimeSession, SessionRegistry, SessionStatus


def adapter(harness_id: str, *, streaming: bool = False, response=None):
    metadata = HarnessMetadata(harness_id, RuntimeKind.AGENT, "1.0")

    def invoke(request):
        if response is not None:
            return response(request)
        return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output=harness_id)

    return CallbackHarnessAdapter(metadata, RuntimeCapabilities(streaming=streaming), invoke)


def test_discovery_is_deterministic_and_reports_capabilities() -> None:
    registry = HarnessRegistry()
    registry.register(adapter("zeta", streaming=True), enabled=True)
    registry.register(adapter("alpha"), enabled=True)
    gateway = CrossRuntimeGateway(registry)

    discovered = gateway.discover()
    assert [item.harness_id for item in discovered] == ["alpha", "zeta"]
    assert discovered[1].capabilities.streaming is True
    assert all(item.health is HarnessHealth.HEALTHY for item in discovered)


def test_select_requires_streaming_capability_and_preference_is_deterministic() -> None:
    registry = HarnessRegistry()
    registry.register(adapter("plain"), enabled=True)
    registry.register(adapter("stream", streaming=True), enabled=True)
    gateway = CrossRuntimeGateway(registry)

    request = InvocationRequest("echo", "x", "project", streaming=True)
    selected = gateway.select(request)
    assert [item.metadata.harness_id for item in selected] == ["stream"]

    request = InvocationRequest("echo", "x", "project")
    selected = gateway.select(request, preferred_harness="stream")
    assert selected[0].metadata.harness_id == "stream"


def test_retryable_prestart_failure_uses_safe_fallback_and_records_decision() -> None:
    def retryable(request):
        return InvocationResponse(
            request.request_id,
            InvocationStatus.FAILED,
            error=RuntimeError(RuntimeErrorCode.TIMEOUT, "temporary", retryable=True),
        )

    registry = HarnessRegistry()
    registry.register(adapter("primary", response=retryable), enabled=True)
    registry.register(adapter("fallback"), enabled=True)
    gateway = CrossRuntimeGateway(registry)
    request = InvocationRequest("echo", "x", "project")

    response = gateway.invoke(request, preferred_harness="primary")
    assert response.output == "fallback"
    decision = gateway.decisions()[-1]
    assert decision.attempted_harnesses == ("primary", "fallback")
    assert decision.fallback_used is True
    assert decision.reason == "retryable_failure_before_start"


def test_fallback_is_refused_after_execution_started() -> None:
    def started_failure(request):
        return InvocationResponse(
            request.request_id,
            InvocationStatus.FAILED,
            events=(RuntimeEvent(RuntimeEventType.STARTED, request.request_id, 0),),
            error=RuntimeError(RuntimeErrorCode.TIMEOUT, "late", retryable=True),
        )

    registry = HarnessRegistry()
    registry.register(adapter("primary", response=started_failure), enabled=True)
    registry.register(adapter("fallback"), enabled=True)
    gateway = CrossRuntimeGateway(registry)
    response = gateway.invoke(InvocationRequest("echo", "x", "project"), preferred_harness="primary")
    assert response.status is InvocationStatus.FAILED
    assert gateway.decisions()[-1].attempted_harnesses == ("primary",)


def test_repeated_failures_quarantine_harness_and_probe_recovers() -> None:
    def fail(request):
        return InvocationResponse(
            request.request_id,
            InvocationStatus.FAILED,
            error=RuntimeError(RuntimeErrorCode.TIMEOUT, "temporary", retryable=True),
        )

    registry = HarnessRegistry()
    registry.register(adapter("bad", response=fail), enabled=True)
    registry.register(adapter("good"), enabled=True)
    gateway = CrossRuntimeGateway(registry, quarantine_after=2, quarantine_seconds=60)
    for _ in range(2):
        response = gateway.invoke(InvocationRequest("echo", "x", "project"), preferred_harness="bad")
        assert response.output == "good"
    assert next(item for item in gateway.discover() if item.harness_id == "bad").health is HarnessHealth.QUARANTINED

    gateway = CrossRuntimeGateway(registry, health_probe=lambda _: True, quarantine_after=2)
    assert gateway.probe("bad") is HarnessHealth.HEALTHY


def test_session_binding_prevents_cross_project_or_cross_harness_use() -> None:
    registry = HarnessRegistry()
    registry.register(adapter("a"), enabled=True)
    registry.register(adapter("b"), enabled=True)
    sessions = SessionRegistry()
    gateway = CrossRuntimeGateway(registry, sessions)
    session = gateway.open_session(RuntimeSession("s1", "project-a", "a"))

    request = InvocationRequest("echo", "x", "project-a", session_id=session.session_id)
    assert gateway.invoke(request).output == "a"

    bad = InvocationRequest("echo", "x", "project-b", session_id=session.session_id)
    try:
        gateway.invoke(bad)
    except (PermissionError, KeyError, ValueError):
        pass
    else:
        raise AssertionError("expected session isolation rejection")


def test_explicit_session_migration_closes_old_binding_and_creates_new_one() -> None:
    registry = HarnessRegistry()
    registry.register(adapter("a"), enabled=True)
    registry.register(adapter("b"), enabled=True)
    sessions = SessionRegistry()
    gateway = CrossRuntimeGateway(registry, sessions)
    gateway.open_session(RuntimeSession("s1", "project-a", "a"))

    migrated = gateway.migrate_session("s1", project_id="project-a", from_harness="a", to_harness="b")
    assert migrated.harness_id == "b"
    assert migrated.session_id != "s1"
    assert sessions.get("s1").status is SessionStatus.CLOSED
    assert sessions.get(migrated.session_id).harness_id == "b"


def test_no_candidate_fails_closed_when_all_are_disabled() -> None:
    registry = HarnessRegistry()
    registry.register(adapter("disabled"), enabled=False)
    gateway = CrossRuntimeGateway(registry)
    try:
        gateway.select(InvocationRequest("echo", "x", "project"))
    except LookupError as exc:
        assert "no healthy enabled harness" in str(exc)
    else:
        raise AssertionError("expected fail-closed selection")


class _Portable:
    def __init__(self, descriptor):
        self.descriptor = descriptor

    def health(self) -> bool:
        return True


def test_portable_adapter_registry_covers_all_v4_resource_kinds() -> None:
    registry = PortableAdapterRegistry()
    for kind in PortableAdapterKind:
        descriptor = PortableAdapterDescriptor(f"{kind.value}-adapter", kind, "1.0", ("read",))
        registry.register(_Portable(descriptor), enabled=True)
    assert {item.kind for item in registry.discover()} == set(PortableAdapterKind)
    assert len(registry.enabled(kind=PortableAdapterKind.CONTEXT)) == 1


def test_portable_adapter_rejects_duplicate_capabilities_and_registry_ids() -> None:
    try:
        descriptor = PortableAdapterDescriptor("context", PortableAdapterKind.CONTEXT, "1.0", ("read", "read"))
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        registry = PortableAdapterRegistry()
        registry.register(_Portable(descriptor))
        try:
            registry.register(_Portable(descriptor))
        except ValueError as exc:
            assert "duplicate" in str(exc)
        else:
            raise AssertionError("expected duplicate adapter rejection")


def test_route_decision_fingerprint_does_not_include_request_input() -> None:
    registry = HarnessRegistry()
    registry.register(adapter("a"), enabled=True)
    gateway = CrossRuntimeGateway(registry)
    response = gateway.invoke(InvocationRequest("echo", {"secret": "do-not-store"}, "project"))
    assert response.output == "a"
    assert "do-not-store" not in gateway.decisions()[-1].decision_id
