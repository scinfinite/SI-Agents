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
    def blocking_requirements(self) -> tuple[RequirementResult, ...]:
        return tuple(item for item in self.requirements if item.blocking)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible, secret-free representation."""
        return {
            "kind": self.kind.value,
            "status": self.status.value,
            "architecture": self.architecture,
            "python_version": self.python_version,
            "home": self.home,
            "prefix": self.prefix,
            "requirements": [
                {
                    "name": item.name,
                    "required": item.required,
                    "present": item.present,
                    "detail": item.detail,
                }
                for item in self.requirements
            ],
            "open_code_available": self.open_code_available,
            "omni_route_configured": self.omni_route_configured,
            "omni_route_healthy": self.omni_route_healthy,
        }
