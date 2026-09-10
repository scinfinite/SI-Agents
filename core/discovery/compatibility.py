from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CompatibilityResult:
    technology: str
    compatible: bool
    reason: str
    evidence: tuple[str, ...] = ()


def check_declared_toolchain(root: Path, technology: str, markers: tuple[str, ...]) -> CompatibilityResult:
    """Check compatibility from repository declarations without executing untrusted code."""
    if not technology.strip():
        raise ValueError("Technology must not be empty")
    if not root.is_dir():
        raise ValueError("Compatibility root must be an existing directory")
    matches = tuple(marker for marker in markers if _exists(root, marker))
    if not matches:
        return CompatibilityResult(technology, False, "No declared compatibility marker found")
    return CompatibilityResult(
        technology,
        True,
        "Declared toolchain marker found",
        evidence=matches,
    )


def _exists(root: Path, marker: str) -> bool:
    if "*" in marker:
        return any(root.glob(marker))
    return (root / marker).is_file()
