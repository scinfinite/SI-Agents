"""Immutable evidence records with explicit epistemic state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
import uuid


EVIDENCE_VERSION = "v1"


class EvidenceKind(StrEnum):
    FACT = "fact"
    OBSERVATION = "observation"
    INFERENCE = "inference"
    UNCERTAINTY = "uncertainty"


class VerificationState(StrEnum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    SUPERSEDED = "superseded"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """A provenance-bearing claim; recording evidence never executes anything."""

    id: str
    claim: str
    kind: EvidenceKind
    source: str
    confidence: float
    verification: VerificationState = VerificationState.UNVERIFIED
    run_id: str | None = None
    provenance: tuple[str, ...] = ()
    related_ids: tuple[str, ...] = ()
    supersedes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("evidence id is required")
        if not self.claim.strip():
            raise ValueError("evidence claim is required")
        if not self.source.strip():
            raise ValueError("evidence source is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("evidence confidence must be between 0 and 1")
        if self.kind is EvidenceKind.UNCERTAINTY and self.verification is VerificationState.VERIFIED:
            raise ValueError("uncertainty cannot be marked verified")

    @classmethod
    def new(
        cls,
        *,
        claim: str,
        kind: EvidenceKind,
        source: str,
        confidence: float,
        verification: VerificationState = VerificationState.UNVERIFIED,
        run_id: str | None = None,
        provenance: tuple[str, ...] = (),
        related_ids: tuple[str, ...] = (),
        supersedes: str | None = None,
    ) -> "EvidenceRecord":
        return cls(
            id=f"ev_{uuid.uuid4().hex}", claim=claim, kind=kind, source=source,
            confidence=confidence, verification=verification, run_id=run_id,
            provenance=provenance, related_ids=related_ids, supersedes=supersedes,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": EVIDENCE_VERSION,
            "id": self.id,
            "claim": self.claim,
            "kind": self.kind.value,
            "source": self.source,
            "confidence": self.confidence,
            "verification": self.verification.value,
            "run_id": self.run_id,
            "provenance": list(self.provenance),
            "related_ids": list(self.related_ids),
            "supersedes": self.supersedes,
            "created_at": self.created_at.isoformat(),
        }
