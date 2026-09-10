from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4


class BenchmarkStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class BenchmarkRun:
    name: str
    score: float
    id: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Benchmark name must not be empty")
        if self.score < 0.0:
            raise ValueError("Benchmark score must not be negative")
        if not self.id:
            object.__setattr__(self, "id", uuid4().hex)


@dataclass(frozen=True)
class BenchmarkComparison:
    name: str
    before: float
    after: float
    delta: float
    status: BenchmarkStatus

    @property
    def improved(self) -> bool:
        return self.delta > 0.0


class Benchmark:
    """Compare independently executed before/after measurements."""

    def __init__(self, name: str, run: Callable[[], float]) -> None:
        if not name.strip():
            raise ValueError("Benchmark name must not be empty")
        self.name = name
        self._run = run

    def execute(self) -> BenchmarkRun:
        try:
            score = float(self._run())
        except Exception as exc:
            raise RuntimeError(f"Benchmark execution failed: {exc}") from exc
        return BenchmarkRun(self.name, score)

    def compare(self, before: BenchmarkRun, after: BenchmarkRun) -> BenchmarkComparison:
        if before.name != self.name or after.name != self.name:
            raise ValueError("Benchmark runs do not match this benchmark")
        delta = after.score - before.score
        return BenchmarkComparison(
            self.name,
            before.score,
            after.score,
            delta,
            BenchmarkStatus.PASSED if after.score >= before.score else BenchmarkStatus.FAILED,
        )

    @staticmethod
    def evaluate(runs: tuple[BenchmarkRun, ...]) -> BenchmarkStatus:
        if not runs:
            return BenchmarkStatus.BLOCKED
        return BenchmarkStatus.PASSED
