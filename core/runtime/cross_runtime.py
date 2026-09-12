"""Cross-runtime and cross-harness routing authority.

The gateway normalizes harness discovery, health, capability matching, session
binding, deterministic selection, and safe pre-start fallback. It never grants
capabilities or mutates SI Core execution state.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from hashlib import sha256
import json
from typing import Callable

from core.runtime.models import InvocationRequest, InvocationResponse, InvocationStatus, RuntimeCapabilities
from core.runtime.protocol import HarnessAdapter
from core.runtime.registry import HarnessRegistry
from core.runtime.session import RuntimeSession, SessionRegistry

_MAX_ID = 128
_MAX_FAILURES = 8


class HarnessHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"


@dataclass(frozen=True)
class HarnessDescriptor:
    harness_id: str
    kind: str
    version: str
    capabilities: RuntimeCapabilities
    enabled: bool
    health: HarnessHealth
    failure_count: int
    quarantined_until: datetime | None = None


@dataclass(frozen=True)
class RouteDecision:
    request_id: str
    project_id: str
    selected_harness: str
    attempted_harnesses: tuple[str, ...]
    fallback_used: bool
    reason: str
    decision_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class _HealthState:
    failures: int = 0
    health: HarnessHealth = HarnessHealth.HEALTHY
    quarantined_until: datetime | None = None


HealthProbe = Callable[[HarnessAdapter], bool]


def _validate_identifier(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > _MAX_ID:
        raise ValueError(f"{field_name} must be a bounded non-empty string")


def _safe_fingerprint(request: InvocationRequest) -> str:
    """Fingerprint routing inputs without serializing arbitrary sensitive values."""
    envelope = {
        "capability_id": request.capability_id,
        "project_id": request.project_id,
        "session_id": request.session_id,
        "streaming": request.streaming,
        "metadata": list(request.metadata),
    }
    return sha256(json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class CrossRuntimeGateway:
    """Select and invoke enabled harnesses while preserving SI Core authority."""

    def __init__(
        self,
        registry: HarnessRegistry,
        sessions: SessionRegistry | None = None,
        *,
        health_probe: HealthProbe | None = None,
        quarantine_after: int = 3,
        quarantine_seconds: int = 30,
    ) -> None:
        if quarantine_after < 1 or quarantine_after > _MAX_FAILURES:
            raise ValueError("quarantine_after out of bounds")
        if quarantine_seconds < 1 or quarantine_seconds > 3600:
            raise ValueError("quarantine_seconds out of bounds")
        self._registry = registry
        self._sessions = sessions
        self._health_probe = health_probe
        self._quarantine_after = quarantine_after
        self._quarantine_seconds = quarantine_seconds
        self._health: dict[str, _HealthState] = {}
        self._decisions: list[RouteDecision] = []

    def discover(self) -> tuple[HarnessDescriptor, ...]:
        """Return deterministic, non-secret capability/health discovery data."""
        now = datetime.now(UTC)
        descriptors: list[HarnessDescriptor] = []
        for adapter in self._registry.all():
            state = self._state(adapter.metadata.harness_id)
            health = state.health
            if state.quarantined_until is not None and now >= state.quarantined_until:
                state.health = HarnessHealth.DEGRADED
                state.quarantined_until = None
                health = state.health
            descriptors.append(
                HarnessDescriptor(
                    adapter.metadata.harness_id,
                    adapter.metadata.kind.value,
                    adapter.metadata.version,
                    adapter.capabilities,
                    self._registry.is_enabled(adapter.metadata.harness_id),
                    health,
                    state.failures,
                    state.quarantined_until,
                )
            )
        return tuple(descriptors)

    def probe(self, harness_id: str) -> HarnessHealth:
        _validate_identifier(harness_id, "harness_id")
        adapter = self._registry.get(harness_id)
        state = self._state(harness_id)
        if self._health_probe is None:
            return state.health
        try:
            healthy = bool(self._health_probe(adapter))
        except Exception:
            healthy = False
        if healthy:
            state.failures = 0
            state.health = HarnessHealth.HEALTHY
            state.quarantined_until = None
        else:
            self._record_failure(harness_id)
        return state.health

    def select(
        self,
        request: InvocationRequest,
        *,
        preferred_harness: str | None = None,
    ) -> tuple[HarnessAdapter, ...]:
        """Return deterministic candidates satisfying request capabilities."""
        session_harness: str | None = None
        if request.session_id:
            if self._sessions is None:
                raise RuntimeError("session registry is required for session-bound requests")
            session = self._sessions.get(request.session_id)
            if session is None:
                raise KeyError(request.session_id)
            if session.status.value != "active" or session.project_id != request.project_id:
                raise PermissionError("session isolation mismatch")
            session_harness = session.harness_id
        candidates = []
        required_streaming = request.streaming
        for adapter in self._registry.enabled():
            harness_id = adapter.metadata.harness_id
            state = self._state(harness_id)
            if state.health is HarnessHealth.QUARANTINED:
                continue
            if session_harness is not None and harness_id != session_harness:
                continue
            if required_streaming and not adapter.capabilities.streaming:
                continue
            candidates.append(adapter)
        if not candidates:
            raise LookupError("no healthy enabled harness satisfies request")
        preferred = preferred_harness.strip() if preferred_harness else None
        if session_harness is not None and preferred is not None and preferred != session_harness:
            raise PermissionError("preferred harness conflicts with session binding")
        candidates.sort(
            key=lambda adapter: (
                0 if preferred and adapter.metadata.harness_id == preferred else 1,
                0 if adapter.capabilities.streaming == required_streaming else 1,
                adapter.metadata.harness_id,
            )
        )
        return tuple(candidates)

    def invoke(self, request: InvocationRequest, *, preferred_harness: str | None = None) -> InvocationResponse:
        candidates = self.select(request, preferred_harness=preferred_harness)
        attempted: list[str] = []
        fallback_used = False
        last_response: InvocationResponse | None = None
        reason = "primary"
        for index, adapter in enumerate(candidates):
            harness_id = adapter.metadata.harness_id
            attempted.append(harness_id)
            try:
                response = adapter.invoke(request)
            except Exception:
                self._record_failure(harness_id)
                if index + 1 == len(candidates):
                    raise
                fallback_used = True
                reason = "transport_failure_before_response"
                continue
            last_response = response
            if response.request_id != request.request_id:
                self._record_failure(harness_id)
                raise ValueError("harness response correlation mismatch")
            if self._can_fallback(response) and index + 1 < len(candidates):
                self._record_failure(harness_id)
                fallback_used = True
                reason = "retryable_failure_before_start"
                continue
            if response.status is InvocationStatus.FAILED:
                self._record_failure(harness_id)
            else:
                self._record_success(harness_id)
            break
        if last_response is None:
            raise RuntimeError("all harness candidates failed before producing a response")
        self._record_decision(request, attempted, fallback_used, attempted[-1], reason)
        return last_response

    def open_session(self, session: RuntimeSession) -> RuntimeSession:
        """Bind a session to one project and one harness; migration is explicit."""
        _validate_identifier(session.project_id, "project_id")
        adapter = self._registry.get(session.harness_id)
        if adapter is None or not self._registry.is_enabled(session.harness_id):
            raise PermissionError("harness is unavailable")
        if self._sessions is None:
            raise RuntimeError("session registry is not configured")
        return self._sessions.create(session)

    def migrate_session(self, session_id: str, *, project_id: str, from_harness: str, to_harness: str) -> RuntimeSession:
        """Create an explicit replacement session; never silently changes binding."""
        if self._sessions is None:
            raise RuntimeError("session registry is not configured")
        _validate_identifier(project_id, "project_id")
        _validate_identifier(from_harness, "from_harness")
        _validate_identifier(to_harness, "to_harness")
        current = self._sessions.require(session_id, project_id=project_id, harness_id=from_harness)
        target = self._registry.get(to_harness)
        if target is None or not self._registry.is_enabled(to_harness):
            raise PermissionError("target harness is unavailable")
        replacement_id = sha256(f"{session_id}:{to_harness}".encode()).hexdigest()[:32]
        replacement = RuntimeSession(replacement_id, project_id, to_harness)
        self._sessions.close(current.session_id)
        return self._sessions.create(replacement)

    def decisions(self) -> tuple[RouteDecision, ...]:
        return tuple(self._decisions)

    def _state(self, harness_id: str) -> _HealthState:
        return self._health.setdefault(harness_id, _HealthState())

    def _record_failure(self, harness_id: str) -> None:
        state = self._state(harness_id)
        state.failures = min(_MAX_FAILURES, state.failures + 1)
        state.health = HarnessHealth.DEGRADED
        if state.failures >= self._quarantine_after:
            state.health = HarnessHealth.QUARANTINED
            state.quarantined_until = datetime.now(UTC) + timedelta(seconds=self._quarantine_seconds)

    def _record_success(self, harness_id: str) -> None:
        state = self._state(harness_id)
        state.failures = 0
        state.health = HarnessHealth.HEALTHY
        state.quarantined_until = None

    @staticmethod
    def _can_fallback(response: InvocationResponse) -> bool:
        if response.status is not InvocationStatus.FAILED or response.error is None or not response.error.retryable:
            return False
        return not any(event.type.value in {"started", "delta", "tool_call", "tool_result"} for event in response.events)

    def _record_decision(
        self,
        request: InvocationRequest,
        attempted: list[str],
        fallback_used: bool,
        selected: str,
        reason: str,
    ) -> None:
        decision_id = sha256(
            f"{request.request_id}:{request.project_id}:{_safe_fingerprint(request)}:{','.join(attempted)}".encode()
        ).hexdigest()
        decision = RouteDecision(
            request.request_id,
            request.project_id,
            selected,
            tuple(attempted),
            fallback_used,
            reason,
            decision_id,
        )
        self._decisions.append(decision)
        if len(self._decisions) > 1024:
            del self._decisions[:-1024]
