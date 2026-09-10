from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4


class HandoffStatus(StrEnum):
    CREATED = "created"
    VALID = "valid"
    INVALID = "invalid"
    IMPORTED = "imported"


@dataclass(frozen=True)
class HandoffEnvelope:
    """Portable workflow state; intentionally excludes credentials and host secrets."""

    schema: str = "si.handoff.v1"
    handoff_id: str = field(default_factory=lambda: str(uuid4()))
    source_environment: str = "unknown"
    source_workspace: str | None = None
    target_environment: str | None = None
    project_id: str | None = None
    team_id: str | None = None
    execution_id: str | None = None
    session_id: str | None = None
    objective: str | None = None
    task_status: dict[str, str] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    checkpoints: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    created_at: str = ""
    status: HandoffStatus = HandoffStatus.CREATED

    def __post_init__(self) -> None:
        if self.schema != "si.handoff.v1":
            raise ValueError("unsupported handoff schema")
        if not self.handoff_id.strip():
            raise ValueError("handoff_id is required")
        if (
            self.target_environment == self.source_environment
            and self.source_environment != "unknown"
        ):
            raise ValueError("source and target environments must differ for a cross-environment handoff")
        if any(value < 0 for value in self.attempts.values()):
            raise ValueError("handoff attempts cannot be negative")
        _reject_secret_keys(self.context)
        _reject_secret_keys(self.results)

    def payload(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "handoff_id": self.handoff_id,
            "source_environment": self.source_environment,
            "source_workspace": self.source_workspace,
            "target_environment": self.target_environment,
            "project_id": self.project_id,
            "team_id": self.team_id,
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "objective": self.objective,
            "task_status": dict(sorted(self.task_status.items())),
            "attempts": dict(sorted(self.attempts.items())),
            "context": self.context,
            "results": self.results,
            "checkpoints": list(self.checkpoints),
            "evidence_ids": list(self.evidence_ids),
            "created_at": self.created_at,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
        return hashlib.sha256(encoded).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        data = self.payload()
        data["status"] = self.status.value
        data["sha256"] = self.digest()
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> HandoffEnvelope:
        if not isinstance(payload, dict):
            raise TypeError("handoff must be a JSON object")
        if payload.get("schema") != "si.handoff.v1":
            raise ValueError("unsupported handoff schema")
        supplied_digest = payload.get("sha256")
        fields = dict(payload)
        fields.pop("sha256", None)
        fields.pop("status", None)
        names = (
            "schema", "handoff_id", "source_environment", "source_workspace",
            "target_environment", "project_id", "team_id", "execution_id",
            "session_id", "objective", "task_status", "attempts", "context",
            "results", "checkpoints", "evidence_ids", "created_at",
        )
        envelope = cls(**{key: fields.get(key) for key in names})
        if supplied_digest != envelope.digest():
            raise ValueError("handoff integrity check failed")
        return cls(**{**envelope.__dict__, "status": HandoffStatus.VALID})


def _reject_secret_keys(value: object) -> None:
    if not isinstance(value, dict):
        return
    secret_terms = (
        "api_key", "apikey", "token", "password", "secret", "credential", "authorization"
    )
    for key, item in value.items():
        normalized = str(key).lower().replace("-", "_")
        if any(term in normalized for term in secret_terms):
            raise ValueError(f"handoff refuses secret-like field: {key}")
        _reject_secret_keys(item)
