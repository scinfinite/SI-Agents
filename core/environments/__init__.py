"""Environment detection and runtime readiness primitives."""

from core.environments.models import (
    EnvironmentKind,
    EnvironmentReport,
    EnvironmentStatus,
    RequirementResult,
)
from core.environments.termux import TermuxRuntime

__all__ = [
    "EnvironmentKind",
    "EnvironmentReport",
    "EnvironmentStatus",
    "RequirementResult",
    "TermuxRuntime",
]
