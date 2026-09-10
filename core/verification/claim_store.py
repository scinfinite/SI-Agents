from __future__ import annotations

from dataclasses import replace

from core.verification.claims import Claim


class ClaimStore:
    """Append-only-by-default claim registry with explicit immutable updates."""

    def __init__(self) -> None:
        self._claims: dict[str, Claim] = {}

    def record(self, claim: Claim) -> Claim:
        if claim.id in self._claims:
            raise ValueError(f"Claim ID already exists: {claim.id}")
        self._claims[claim.id] = claim
        return claim

    def get(self, claim_id: str) -> Claim:
        try:
            return self._claims[claim_id]
        except KeyError as exc:
            raise KeyError(f"Unknown claim: {claim_id}") from exc

    def all(self) -> tuple[Claim, ...]:
        return tuple(self._claims.values())

    def attach_evidence(self, claim_id: str, evidence_ids: tuple[str, ...], confidence: float) -> Claim:
        claim = self.get(claim_id)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Claim confidence must be between 0 and 1")
        merged = tuple(dict.fromkeys((*claim.evidence_ids, *evidence_ids)))
        updated = replace(claim, evidence_ids=merged, confidence=confidence)
        self._claims[claim_id] = updated
        return updated
