"""Dependency-free health and readiness checks."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthReport:
    status: HealthStatus
    checks: tuple[tuple[str, HealthStatus, str], ...]


class ReadinessChecker:
    """Run named checks and fail closed when a check raises or returns false."""

    def __init__(self, checks: dict[str, Callable[[], bool]]) -> None:
        if any(not name.strip() for name in checks):
            raise ValueError("check names must not be empty")
        self._checks = dict(checks)

    def check(self) -> HealthReport:
        results: list[tuple[str, HealthStatus, str]] = []
        for name in sorted(self._checks):
            try:
                ok = bool(self._checks[name]())
            except Exception:  # noqa: BLE001 - health boundary must fail closed
                results.append((name, HealthStatus.UNHEALTHY, "check failed"))
                continue
            results.append(
                (name, HealthStatus.HEALTHY if ok else HealthStatus.UNHEALTHY, "ok" if ok else "not ready")
            )
        if any(status is HealthStatus.UNHEALTHY for _, status, _ in results):
            overall = HealthStatus.UNHEALTHY
        elif any(status is HealthStatus.DEGRADED for _, status, _ in results):
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY
        return HealthReport(overall, tuple(results))
