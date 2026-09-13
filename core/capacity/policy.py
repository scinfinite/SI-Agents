"""Explicit workload-capacity policy with mobile-safe defaults.

The policy controls SI-Agents local work admission. It does not claim to control
CPU/GPU temperature inside external harnesses or model providers; those remain
separate processes/services. High-cost work on Termux is rejected unless the
request explicitly targets a desktop or Codespace runtime.
"""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class CapacityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CapacityTarget(StrEnum):
    LOCAL = "local"
    TERMUX = "termux"
    DESKTOP = "desktop"
    CODESPACE = "codespace"
    REMOTE = "remote"


@dataclass(frozen=True)
class CapacityDecision:
    level: CapacityLevel
    target: CapacityTarget
    allowed: bool
    warning: str | None
    reasons: tuple[str, ...]
    max_workers: int
    max_parallel_requests: int
    compile_allowed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "level": self.level.value,
            "target": self.target.value,
            "allowed": self.allowed,
            "warning": self.warning,
            "reasons": list(self.reasons),
            "limits": {
                "max_workers": self.max_workers,
                "max_parallel_requests": self.max_parallel_requests,
                "compile_allowed": self.compile_allowed,
            },
        }


class CapacityPolicy:
    """Classify work and apply conservative host-specific admission limits."""

    _HIGH_MARKERS = (
        "compile", "build", "benchmark", "train", "index-all", "full-suite",
        "bundle", "package-release", "large-refactor", "migration", "codegen",
    )
    _MEDIUM_MARKERS = (
        "test", "lint", "review", "analyze", "scan", "search", "debug", "inspect",
    )
    _COMPILE_MARKERS = ("compile", "build", "bundle", "package", "codegen", "cargo", "gradle", "maven")

    def detect_target(self, environ: Mapping[str, str] | None = None) -> CapacityTarget:
        env = os.environ if environ is None else environ
        if env.get("TERMUX_VERSION") or "/com.termux/" in env.get("PREFIX", ""):
            return CapacityTarget.TERMUX
        if env.get("CODESPACES"):
            return CapacityTarget.CODESPACE
        return CapacityTarget.DESKTOP if platform.system() != "" else CapacityTarget.LOCAL

    def classify(self, payload: Mapping[str, object]) -> CapacityLevel:
        explicit = payload.get("capacity")
        if isinstance(explicit, str):
            try:
                return CapacityLevel(explicit.lower())
            except ValueError as exc:
                raise ValueError("capacity must be one of: low, medium, high") from exc
        haystack = " ".join(str(payload.get(key, "")) for key in ("action", "subject", "workload", "operation")).lower()
        if any(marker in haystack for marker in self._HIGH_MARKERS):
            return CapacityLevel.HIGH
        if any(marker in haystack for marker in self._MEDIUM_MARKERS):
            return CapacityLevel.MEDIUM
        return CapacityLevel.LOW

    def evaluate(self, payload: Mapping[str, object], *, target: CapacityTarget | None = None) -> CapacityDecision:
        level = self.classify(payload)
        target = target or self.detect_target()
        compile_requested = bool(payload.get("compile", False)) or any(
            marker in " ".join(str(payload.get(key, "")).lower() for key in ("action", "subject", "workload", "operation"))
            for marker in self._COMPILE_MARKERS
        )
        if target is CapacityTarget.TERMUX:
            limits = {CapacityLevel.LOW: (1, 1), CapacityLevel.MEDIUM: (2, 2), CapacityLevel.HIGH: (0, 0)}
            workers, parallel = limits[level]
            if level is CapacityLevel.HIGH:
                return CapacityDecision(
                    level, target, False,
                    "High-capacity work is disabled on Termux. Use a desktop or Codespace target.",
                    ("mobile_local_high_capacity_block", "prefer_remote_execution_for_heavy_work"),
                    workers, parallel, False,
                )
            warning = "Termux-safe bounded mode: avoid long-running local builds and parallel model processes." if level is CapacityLevel.MEDIUM else None
            return CapacityDecision(level, target, True, warning, ("bounded_mobile_execution",), workers, parallel, False)
        if target is CapacityTarget.DESKTOP:
            workers = {CapacityLevel.LOW: 2, CapacityLevel.MEDIUM: 4, CapacityLevel.HIGH: 8}[level]
            parallel = {CapacityLevel.LOW: 2, CapacityLevel.MEDIUM: 4, CapacityLevel.HIGH: 8}[level]
            warning = "High-capacity work may increase CPU/GPU load; monitor system thermals." if level is CapacityLevel.HIGH else None
            return CapacityDecision(level, target, True, warning, ("desktop_capacity_available",), workers, parallel, True)
        if target is CapacityTarget.CODESPACE:
            workers = {CapacityLevel.LOW: 2, CapacityLevel.MEDIUM: 4, CapacityLevel.HIGH: 8}[level]
            parallel = workers
            return CapacityDecision(level, target, True, None, ("codespace_offload_target",), workers, parallel, True)
        workers = {CapacityLevel.LOW: 1, CapacityLevel.MEDIUM: 2, CapacityLevel.HIGH: 4}[level]
        parallel = workers
        warning = "High-capacity work is permitted only when the local host can sustain it; prefer a remote target." if level is CapacityLevel.HIGH else None
        return CapacityDecision(level, target, True, warning, ("conservative_local_default",), workers, parallel, not compile_requested or target is not CapacityTarget.LOCAL)

    def describe(self) -> dict[str, object]:
        target = self.detect_target()
        return {
            "current_target": target.value,
            "levels": {
                "low": "bounded local inspection, metadata, navigation, and short edits",
                "medium": "bounded analysis, tests, lint, review, and short-running workflows",
                "high": "compilation, large builds, benchmarks, large indexes, and other sustained workloads",
            },
            "termux": {
                "low": "allowed, one worker",
                "medium": "allowed, two workers, bounded parallelism",
                "high": "blocked locally; target desktop or Codespace",
                "compilation": "blocked locally",
            },
            "note": "The policy reduces SI-Agents local load; it cannot guarantee a device temperature because external harnesses and model providers run outside this policy.",
        }
