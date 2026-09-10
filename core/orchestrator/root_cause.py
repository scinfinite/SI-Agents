from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class RootCauseConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class CauseNode:
    statement: str
    evidence: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("Cause statement must not be empty")


@dataclass(frozen=True)
class RootCauseAnalysis:
    problem: str
    root_cause: str
    causal_chain: tuple[CauseNode, ...]
    confidence: RootCauseConfidence
    evidence: tuple[str, ...] = ()
    alternatives_rejected: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: uuid4().hex)


class RootCauseEngine:
    """Provides deterministic structural checks for evidence-backed RCA results."""

    def analyze(
        self,
        *,
        problem: str,
        causes: tuple[CauseNode, ...],
        root_cause: str,
        evidence: tuple[str, ...],
        alternatives_rejected: tuple[str, ...] = (),
    ) -> RootCauseAnalysis:
        if not problem.strip() or not root_cause.strip():
            raise ValueError("Problem and root cause must not be empty")
        ids = {node.id for node in causes}
        for node in causes:
            if any(parent not in ids for parent in node.parents):
                raise ValueError("Cause parent must reference a known cause node")
        if not causes:
            confidence = RootCauseConfidence.LOW
        elif evidence and len(evidence) >= 2:
            confidence = RootCauseConfidence.HIGH
        else:
            confidence = RootCauseConfidence.MEDIUM
        return RootCauseAnalysis(
            problem=problem,
            root_cause=root_cause,
            causal_chain=causes,
            confidence=confidence,
            evidence=evidence,
            alternatives_rejected=alternatives_rejected,
        )
