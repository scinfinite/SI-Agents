"""Evidence read/write boundary used by API and operator surfaces."""

from __future__ import annotations

from typing import Any

from .models import EvidenceKind, EvidenceRecord, VerificationState
from .store import EvidenceStore


class EvidenceService:
    """Expose evidence facts without executing or authorizing downstream work."""

    def __init__(self, path: str) -> None:
        self.store = EvidenceStore(path)

    def list(self, *, run_id: str | None = None) -> list[dict[str, Any]]:
        records = self.store.records()
        if run_id is not None:
            records = tuple(item for item in records if item.run_id == run_id)
        return [item.as_dict() for item in records]

    def get(self, evidence_id: str) -> dict[str, Any]:
        return self.store.get(evidence_id).as_dict()

    def record(self, payload: dict[str, Any]) -> dict[str, Any]:
        claim = payload.get("claim")
        source = payload.get("source")
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("claim is required")
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source is required")
        kind = EvidenceKind(payload.get("kind", EvidenceKind.OBSERVATION.value))
        verification = VerificationState(payload.get("verification", VerificationState.UNVERIFIED.value))
        confidence = float(payload.get("confidence", 0.0))
        provenance = payload.get("provenance", [])
        related_ids = payload.get("related_ids", [])
        if not isinstance(provenance, list) or not all(isinstance(x, str) for x in provenance):
            raise ValueError("provenance must be a list of strings")
        if not isinstance(related_ids, list) or not all(isinstance(x, str) for x in related_ids):
            raise ValueError("related_ids must be a list of strings")
        run_id = payload.get("run_id")
        if run_id is not None and not isinstance(run_id, str):
            raise ValueError("run_id must be a string")
        supersedes = payload.get("supersedes")
        if supersedes is not None and not isinstance(supersedes, str):
            raise ValueError("supersedes must be a string")
        record = EvidenceRecord.new(
            claim=claim, kind=kind, source=source, confidence=confidence,
            verification=verification, run_id=run_id, provenance=tuple(provenance),
            related_ids=tuple(related_ids), supersedes=supersedes,
        )
        return self.store.record(record).as_dict()

    def verify(self, evidence_id: str, state: str) -> dict[str, Any]:
        return self.store.update_verification(evidence_id, VerificationState(state)).as_dict()

    def timeline(self, run_id: str) -> dict[str, Any]:
        records = [item for item in self.store.records() if item.run_id == run_id]
        return {
            "run_id": run_id,
            "events": [item.as_dict() for item in records],
            "counts": {
                "total": len(records),
                "facts": sum(item.kind is EvidenceKind.FACT for item in records),
                "observations": sum(item.kind is EvidenceKind.OBSERVATION for item in records),
                "inferences": sum(item.kind is EvidenceKind.INFERENCE for item in records),
                "uncertainties": sum(item.kind is EvidenceKind.UNCERTAINTY for item in records),
                "verified": sum(item.verification is VerificationState.VERIFIED for item in records),
                "contradicted": sum(item.verification is VerificationState.CONTRADICTED for item in records),
                "superseded": sum(item.verification is VerificationState.SUPERSEDED for item in records),
            },
            "note": "Evidence describes recorded claims and provenance; it does not imply downstream execution occurred.",
        }
