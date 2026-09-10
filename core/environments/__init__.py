"""Environment detection and runtime readiness primitives."""

from core.environments.codespace import CodespaceConfig, CodespaceRuntime
from core.environments.models import (
    EnvironmentKind,
    EnvironmentReport,
    EnvironmentStatus,
    RequirementResult,
)
from core.environments.termux import TermuxConfig, TermuxRuntime

__all__ = [
    "CodespaceConfig",
    "CodespaceRuntime",
    "EnvironmentKind",
    "EnvironmentReport",
    "EnvironmentStatus",
    "RequirementResult",
    "TermuxConfig",
    "TermuxRuntime",
]
