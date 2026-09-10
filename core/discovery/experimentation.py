from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    passed: bool
    observation: str


class ExperimentRunner:
    """Runs explicitly supplied, non-destructive discovery experiments."""

    def run(self, name: str, root: Path, experiment: Callable[[Path], str]) -> ExperimentResult:
        if not name.strip():
            raise ValueError("Experiment name must not be empty")
        if not root.is_dir():
            raise ValueError("Experiment root must be an existing directory")
        try:
            observation = experiment(root)
        except Exception as exc:
            return ExperimentResult(name=name, passed=False, observation=f"{type(exc).__name__}: {exc}")
        if not isinstance(observation, str) or not observation.strip():
            return ExperimentResult(name=name, passed=False, observation="empty experiment observation")
        return ExperimentResult(name=name, passed=True, observation=observation.strip())
