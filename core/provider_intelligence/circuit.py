"""Deterministic circuit breaker for unreliable providers."""

from dataclasses import dataclass
from time import monotonic


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    cooldown_seconds: float = 30.0
    _failures: int = 0
    _opened_at: float | None = None

    def __post_init__(self) -> None:
        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be non-negative")

    @property
    def open(self) -> bool:
        if self._opened_at is None:
            return False
        if monotonic() - self._opened_at >= self.cooldown_seconds:
            self._opened_at = None
            self._failures = 0
            return False
        return True

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._opened_at = monotonic()

    def allow(self) -> bool:
        return not self.open
