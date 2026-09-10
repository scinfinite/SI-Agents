"""Atomic local persistence for evidence records."""

from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock

from .models import EvidenceKind, EvidenceRecord, VerificationState


class EvidenceStore:
    """Append/replace evidence atomically without becoming an execution authority."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self._lock = RLock()
        self._records: dict[str, EvidenceRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("version") != "v1":
            raise ValueError("unsupported evidence store version")
        items = payload.get("records", [])
        if not isinstance(items, list):
            raise ValueError("evidence records must be a list")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("invalid evidence record")
            record = EvidenceRecord(
                id=str(item["id"]), claim=str(item["claim"]), kind=EvidenceKind(item["kind"]),
                source=str(item["source"]), confidence=float(item["confidence"]),
                verification=VerificationState(item.get("verification", "unverified")),
                run_id=item.get("run_id"), provenance=tuple(item.get("provenance", [])),
                related_ids=tuple(item.get("related_ids", [])), supersedes=item.get("supersedes"),
            )
            self._records[record.id] = record

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": "v1", "records": [r.as_dict() for r in self.records()]}
        temp = self.path.with_name(f".{self.path.name}.tmp")
        old_umask = os.umask(0o077)
        try:
            temp.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            temp.chmod(0o600)
            os.replace(temp, self.path)
        finally:
            os.umask(old_umask)
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(sorted(self._records.values(), key=lambda item: (item.created_at, item.id)))

    def get(self, evidence_id: str) -> EvidenceRecord:
        with self._lock:
            try:
                return self._records[evidence_id]
            except KeyError as exc:
                raise KeyError(evidence_id) from exc

    def record(self, evidence: EvidenceRecord) -> EvidenceRecord:
        with self._lock:
            if evidence.id in self._records:
                raise ValueError("evidence id already exists")
            if evidence.supersedes:
                prior = self._records.get(evidence.supersedes)
                if prior is None:
                    raise ValueError("superseded evidence does not exist")
                self._records[prior.id] = EvidenceRecord(
                    id=prior.id, claim=prior.claim, kind=prior.kind, source=prior.source,
                    confidence=prior.confidence, verification=VerificationState.SUPERSEDED,
                    run_id=prior.run_id, provenance=prior.provenance, related_ids=prior.related_ids,
                    supersedes=prior.supersedes, created_at=prior.created_at,
                )
            self._records[evidence.id] = evidence
            self._persist()
            return evidence

    def update_verification(self, evidence_id: str, state: VerificationState) -> EvidenceRecord:
        with self._lock:
            current = self.get(evidence_id)
            updated = EvidenceRecord(
                id=current.id, claim=current.claim, kind=current.kind, source=current.source,
                confidence=current.confidence, verification=state, run_id=current.run_id,
                provenance=current.provenance, related_ids=current.related_ids,
                supersedes=current.supersedes, created_at=current.created_at,
            )
            self._records[evidence_id] = updated
            self._persist()
            return updated
