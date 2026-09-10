from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class PatternStatus(str, Enum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    EXPERIMENTAL = "experimental"
    REJECTED = "rejected"


class PatternCategory(str, Enum):
    ARCHITECTURE = "architecture"
    CODING = "coding"
    DEBUGGING = "debugging"
    TESTING = "testing"
    SECURITY = "security"
    DATABASES = "databases"
    NETWORKING = "networking"
    DISTRIBUTED_SYSTEMS = "distributed_systems"
    DEVOPS = "devops"
    AI = "ai"
    AGENT_SYSTEMS = "agent_systems"
    GENERAL = "general"


@dataclass(frozen=True)
class PatternEvidence:
    source: str
    example_id: str
    claim: str
    verified: bool = False
    evidence_id: str | None = None

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.example_id.strip() or not self.claim.strip():
            raise ValueError("Pattern evidence requires source, example ID, and claim")


@dataclass(frozen=True)
class Counterexample:
    example_id: str
    reason: str
    source: str

    def __post_init__(self) -> None:
        if not self.example_id.strip() or not self.reason.strip() or not self.source.strip():
            raise ValueError("Counterexample requires example ID, reason, and source")


@dataclass(frozen=True)
class PatternObservation:
    example_id: str
    source: str
    category: PatternCategory
    problem: str
    context: str
    mechanism: str
    outcome: str
    tags: tuple[str, ...] = ()
    evidence: tuple[PatternEvidence, ...] = ()
    counterexamples: tuple[Counterexample, ...] = ()

    def __post_init__(self) -> None:
        required = (self.example_id, self.source, self.problem, self.context, self.mechanism, self.outcome)
        if any(not value.strip() for value in required):
            raise ValueError("Pattern observation fields must not be blank")


@dataclass(frozen=True)
class EngineeringPattern:
    name: str
    category: PatternCategory
    intent: str
    context: str
    mechanism: str
    applicability: tuple[str, ...]
    contraindications: tuple[str, ...]
    verification_criteria: tuple[str, ...]
    provenance: tuple[str, ...]
    evidence: tuple[PatternEvidence, ...] = ()
    counterexamples: tuple[Counterexample, ...] = ()
    confidence: float = 0.0
    status: PatternStatus = PatternStatus.CANDIDATE
    version: int = 1
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.intent.strip() or not self.context.strip():
            raise ValueError("Pattern name, intent, and context are required")
        if not self.mechanism.strip() or not self.verification_criteria:
            raise ValueError("Pattern mechanism and verification criteria are required")
        if not self.provenance:
            raise ValueError("Pattern requires provenance")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Pattern confidence must be between 0 and 1")
        if self.version < 1:
            raise ValueError("Pattern version must be positive")


@dataclass(frozen=True)
class ValidationResult:
    pattern_id: str
    status: PatternStatus
    confidence: float
    independent_sources: int
    independent_examples: int
    verified_evidence: int
    counterexamples: int
    reasons: tuple[str, ...] = ()

    @property
    def promotable(self) -> bool:
        return self.status is PatternStatus.VALIDATED
