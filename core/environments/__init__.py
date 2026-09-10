"""Environment detection and runtime readiness primitives."""

from core.environments.models import (
    EnvironmentKind,
    EnvironmentReport,
    EnvironmentStatus,
    RequirementResult,
)
from core.environments.termux import TermuxConfig, TermuxRuntime

__all__ = [
    "EnvironmentKind",
    "EnvironmentReport",
    "EnvironmentStatus",
    "RequirementResult",
    "TermuxConfig",
    "TermuxRuntime",
]
