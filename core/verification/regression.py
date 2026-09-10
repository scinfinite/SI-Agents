from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class RegressionStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class RegressionCase:
    name: str
    check: Callable[[], bool] = field(repr=False, compare=False)
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Regression case name must not be empty")


@dataclass(frozen=True)
class RegressionResult:
    case_id: str
    name: str
    status: RegressionStatus
    details: str = ""


@dataclass(frozen=True)
class RegressionSuiteResult:
    status: RegressionStatus
    results: tuple[RegressionResult, ...]

    @property
    def passed(self) -> bool:
        return self.status is RegressionStatus.PASSED


class RegressionSuite:
    """Deterministic regression runner that fails closed on errors."""

    def __init__(self, cases: tuple[RegressionCase, ...] = ()) -> None:
        self._cases: list[RegressionCase] = list(cases)

    def add(self, case: RegressionCase) -> RegressionCase:
        if any(existing.id == case.id for existing in self._cases):
            raise ValueError(f"Duplicate regression case ID: {case.id}")
        if any(existing.name == case.name for existing in self._cases):
            raise ValueError(f"Duplicate regression case name: {case.name}")
        self._cases.append(case)
        return case

    def run(self) -> RegressionSuiteResult:
        results: list[RegressionResult] = []
        for case in self._cases:
            try:
                passed = bool(case.check())
            except Exception as exc:  # noqa: BLE001 - regression exceptions must fail closed.
                results.append(
                    RegressionResult(case.id, case.name, RegressionStatus.FAILED, f"check raised: {exc}")
                )
                continue
            results.append(
                RegressionResult(
                    case.id,
                    case.name,
                    RegressionStatus.PASSED if passed else RegressionStatus.FAILED,
                    "check passed" if passed else "check returned false",
                )
            )
        status = (
            RegressionStatus.PASSED
            if results and all(item.status is RegressionStatus.PASSED for item in results)
            else RegressionStatus.FAILED
        )
        if not results:
            status = RegressionStatus.BLOCKED
        return RegressionSuiteResult(status, tuple(results))
