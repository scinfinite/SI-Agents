"""Fail-closed local execution capacity policy.

The policy is deliberately conservative on Termux/mobile devices. It does not
claim to control device temperature; it limits SI-controlled concurrency and
blocks work classes that are inappropriate for a mobile execution host.
"""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from enum import StrEnum


class CapacityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class CapacityDecision:
    level: CapacityLevel
    workers: int
    allowed: bool
    requires_remote: bool
    warning: str | None = None
    reason: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "level": self.level.value,
            "workers": self.workers,
            "allowed": self.allowed,
            "requires_remote": self.requires_remote,
            "warning": self.warning,
            "reason": self.reason,
        }


class CapacityPolicy:
    """Resolve an explicit capacity profile for the current execution host."""

    LOW_MIN, LOW_MAX = 1, 2
    MEDIUM_MIN, MEDIUM_MAX = 3, 5

    def __init__(self, *, environment: str | None = None) -> None:
        self.environment = environment or detect_environment()

    @property
    def mobile(self) -> bool:
        return self.environment == "termux"

    def decide(
        self,
        level: CapacityLevel | str,
        *,
        workers: int | None = None,
        workload: str = "general",
    ) -> CapacityDecision:
        level = CapacityLevel(str(level).lower())
        normalized_workers = self._workers(level, workers)
        heavy = self._is_heavy_workload(workload)

        if self.mobile and level is CapacityLevel.HIGH:
            return CapacityDecision(
                level, normalized_workers, False, True,
                warning="High-capacity execution is disabled on Termux/mobile; use a desktop or Codespace.",
                reason="mobile-high-capacity-block",
            )
        if self.mobile and heavy:
            return CapacityDecision(
                level, normalized_workers, False, True,
                warning="This workload is build/compile intensive and should run on a desktop or Codespace.",
                reason="mobile-heavy-workload-block",
            )
        if level is CapacityLevel.HIGH:
            return CapacityDecision(
                level, normalized_workers, True, False,
                warning="High-capacity execution may consume substantial CPU, memory, battery, and network resources.",
            )
        warning = (
            "Termux/mobile mode is bounded to reduce sustained device load; device temperature is not controlled by SI-Agents."
            if self.mobile else None
        )
        return CapacityDecision(level, normalized_workers, True, False, warning=warning)

    def _workers(self, level: CapacityLevel, requested: int | None) -> int:
        if level is CapacityLevel.LOW:
            default = 1 if self.mobile else 2
            minimum, maximum = self.LOW_MIN, self.LOW_MAX
        elif level is CapacityLevel.MEDIUM:
            default = 3 if self.mobile else 4
            minimum, maximum = self.MEDIUM_MIN, self.MEDIUM_MAX
        else:
            default, minimum, maximum = 8, 1, 16
        value = default if requested is None else requested
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("workers must be an integer")
        if not minimum <= value <= maximum:
            raise ValueError(f"{level.value} workers must be between {minimum} and {maximum}")
        return value

    @staticmethod
    def _is_heavy_workload(workload: str) -> bool:
        value = workload.strip().casefold()
        heavy_terms = (
            "compile", "compilation", "build", "benchmark", "large-test", "large test",
            "docker", "container-build", "package-native", "native-build", "full-release",
        )
        return any(term in value for term in heavy_terms)


def detect_environment() -> str:
    if os.environ.get("TERMUX_VERSION") or os.environ.get("PREFIX", "").endswith("/com.termux/files/usr"):
        return "termux"
    return "desktop" if platform.system() in {"Windows", "Darwin", "Linux"} else "unknown"


def resolve_from_environment(*, workload: str = "general") -> CapacityDecision:
    """Resolve SI_CAPACITY and SI_WORKERS without ever silently exceeding limits."""
    level = os.environ.get("SI_CAPACITY", "low" if detect_environment() == "termux" else "medium")
    workers_raw = os.environ.get("SI_WORKERS")
    workers = None if workers_raw is None else int(workers_raw)
    return CapacityPolicy().decide(level, workers=workers, workload=workload)
