"""Vendor-neutral environment readiness models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EnvironmentKind(str, Enum):
    """Supported execution environments."""

    TERMUX = "termux"
    CODESPACE = "codespace"
    UNKNOWN = "unknown"


class EnvironmentStatus(str, Enum):
    """Overall readiness state."""

    READY = "ready"
    DEGRADED = "degraded"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class RequirementResult:
    """Result of one environment requirement check."""

    name: str
    required: bool
    present: bool
    detail: str

    @property
    def blocking(self) -> bool:
        return self.required and not self.present


@dataclass(frozen=True)
class EnvironmentReport:
    """Sanitized environment readiness report."""

    kind: EnvironmentKind
    status: EnvironmentStatus
    architecture: str
    python_version: str
    home: str
    prefix: str
    requirements: tuple[RequirementResult, ...]
    open_code_available: bool
    omni_route_configured: bool
    omni_route_healthy: bool | None

    @property
    def ready(self) -> bool:
        return self.status is EnvironmentStatus.READY

    @property
    blocking_requirements(self) -> tuple[RequirementResult, ...]:
        return tuple(item for item in self.requirements if item.blocking)
