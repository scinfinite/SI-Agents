"""Provider health observations used by routing policy."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class HealthObservation:
    provider_id: str
    success: bool
    latency_ms: float
    observed_at: datetime = datetime.now(UTC)

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id must not be empty")
        if self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")


class HealthTracker:
    """Stores bounded recent health observations and exposes a simple success rate."""

    def __init__(self, window: int = 20) -> None:
        if window <= 0:
            raise ValueError("window must be positive")
        self.window = window
        self._observations: dict[str, list[HealthObservation]] = {}

    def record(self, observation: HealthObservation) -> None:
        entries = self._observations.setdefault(observation.provider_id, [])
        entries.append(observation)
        del entries[:-self.window]

    def success_rate(self, provider_id: str) -> float:
        entries = self._observations.get(provider_id, [])
        if not entries:
            return 1.0
        return sum(item.success for item in entries) / len(entries)
