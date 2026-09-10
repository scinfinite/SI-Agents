"""Dependency-free JSON persistence for automation definitions and run history."""

import json
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from core.automation.models import (
    AutomationJob,
    JobState,
    RetryPolicy,
    RunRecord,
    RunStatus,
    Schedule,
    ScheduleKind,
)
from core.automation.registry import AutomationRegistry


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    return value


class AutomationStore:
    """Persist declarative jobs and immutable run records without secrets."""

    def save(self, path: str | Path, registry: AutomationRegistry, runs: tuple[RunRecord, ...] = ()) -> None:
        payload = {
            "jobs": [_encode(asdict(job)) for job in registry.list()],
            "runs": [_encode(asdict(run)) for run in runs],
        }
        Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def load(self, path: str | Path) -> tuple[AutomationRegistry, tuple[RunRecord, ...]]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list) or not isinstance(payload.get("runs"), list):
            raise TypeError("automation store must contain jobs and runs lists")
        registry = AutomationRegistry()
        for raw in payload["jobs"]:
            if not isinstance(raw, dict):
                raise TypeError("job entries must be objects")
            schedule_raw = raw.pop("schedule")
            retry_raw = raw.pop("retry")
            raw["schedule"] = Schedule(
                ScheduleKind(schedule_raw["kind"]),
                datetime.fromisoformat(schedule_raw["next_run_at"]),
                schedule_raw.get("interval_seconds"),
            )
            raw["retry"] = RetryPolicy(**retry_raw)
            raw["state"] = JobState(raw["state"])
            raw["tags"] = tuple(raw.get("tags", ()))
            registry.register(AutomationJob(**raw))
        runs = tuple(
            RunRecord(
                **{
                    **raw,
                    "status": RunStatus(raw["status"]),
                    "started_at": datetime.fromisoformat(raw["started_at"]),
                    "finished_at": datetime.fromisoformat(raw["finished_at"]),
                }
            )
            for raw in payload["runs"]
        )
        return registry, runs
