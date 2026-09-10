from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReadinessStatus(str, Enum):
    READY = "ready"
    NOT_READY = "not_ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ReadinessGate:
    name: str
    passed: bool
    evidence_ids: tuple[str, ...] = ()
    details: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Readiness gate name must not be empty")
        if self.passed and not self.evidence_ids:
            raise ValueError("A passed readiness gate requires evidence")
        if not self.passed and not self.details.strip():
            raise ValueError("A failed readiness gate requires details")


@dataclass(frozen=True)
class ProductionReadiness:
    status: ReadinessStatus
    gates: tuple[ReadinessGate, ...]

    @property
    def ready(self) -> bool:
        return self.status is ReadinessStatus.READY


def evaluate(gates: tuple[ReadinessGate, ...]) -> ProductionReadiness:
    if not gates:
        return ProductionReadiness(ReadinessStatus.BLOCKED, ())
    status = ReadinessStatus.READY if all(gate.passed for gate in gates) else ReadinessStatus.NOT_READY
    return ProductionReadiness(status, gates)
