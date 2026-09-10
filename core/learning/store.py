import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from core.learning.models import (
    EvaluationResult,
    EvidenceItem,
    ImprovementProposal,
    ImprovementStatus,
)


def _encode(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_encode(item) for item in value]
    if isinstance(value, EvidenceItem):
        return {**asdict(value)}
    if isinstance(value, EvaluationResult):
        return _encode(asdict(value))
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    return value


def _decode_evidence(items: list[dict[str, object]]) -> tuple[EvidenceItem, ...]:
    return tuple(EvidenceItem(**item) for item in items)


class ImprovementStore:
    """Dependency-free JSON persistence for auditable improvement proposals."""

    def save(self, path: str | Path, proposals: tuple[ImprovementProposal, ...]) -> None:
        payload = _encode([asdict(item) for item in proposals])
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> tuple[ImprovementProposal, ...]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise TypeError("Improvement store root must be a list")
        result: list[ImprovementProposal] = []
        for raw in data:
            if not isinstance(raw, dict):
                raise TypeError("Improvement store entries must be objects")
            raw = dict(raw)
            raw["status"] = ImprovementStatus(raw["status"])
            raw["created_at"] = datetime.fromisoformat(raw["created_at"])
            raw["evidence"] = _decode_evidence(raw["evidence"])
            if raw.get("evaluation") is not None:
                evaluation = dict(raw["evaluation"])
                evaluation["evaluated_at"] = datetime.fromisoformat(evaluation["evaluated_at"])
                evaluation["evidence"] = _decode_evidence(evaluation["evidence"])
                evaluation["regressions"] = tuple(evaluation["regressions"])
                raw["evaluation"] = EvaluationResult(**evaluation)
            result.append(ImprovementProposal(**raw))
        return tuple(result)
