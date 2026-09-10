from __future__ import annotations

from core.verification.evidence import Evidence


class EvidenceStore:
    """In-memory evidence ledger for the control plane."""

    def __init__(self) -> None:
        self._evidence: dict[str, Evidence] = {}

    def record(self, evidence: Evidence) -> Evidence:
        if evidence.id in self._evidence:
            raise ValueError(f"Evidence ID already exists: {evidence.id}")
        self._evidence[evidence.id] = evidence
        return evidence

    def get(self, evidence_id: str) -> Evidence:
        try:
            return self._evidence[evidence_id]
        except KeyError as exc:
            raise KeyError(f"Unknown evidence: {evidence_id}") from exc

    def all(self) -> tuple[Evidence, ...]:
        return tuple(self._evidence.values())
