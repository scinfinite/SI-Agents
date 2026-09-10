from dataclasses import dataclass
from datetime import UTC, datetime

from core.capabilities.models import Capability
from core.capabilities.registry import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityHealth:
    capability_id: str
    healthy: bool
    score: float
    checked_at: datetime
    reason: str = ""


class CapabilityHealthTracker:
    """Records validated health observations without silently changing status."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        self._checks: dict[str, CapabilityHealth] = {}

    def record(self, capability_id: str, *, score: float, reason: str = "") -> CapabilityHealth:
        self.registry.get(capability_id)
        if not 0.0 <= score <= 1.0:
            raise ValueError("Capability health score must be between 0 and 1")
        check = CapabilityHealth(
            capability_id=capability_id,
            healthy=score > 0.0,
            score=score,
            checked_at=datetime.now(UTC),
            reason=reason,
        )
        self._checks[capability_id] = check
        return check

    def get(self, capability_id: str) -> CapabilityHealth:
        try:
            return self._checks[capability_id]
        except KeyError as exc:
            raise KeyError(f"No health check for capability: {capability_id}") from exc

    def all(self) -> tuple[CapabilityHealth, ...]:
        return tuple(self._checks.values())
