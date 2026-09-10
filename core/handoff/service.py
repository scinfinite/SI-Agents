from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from agents.base import AgentResult
from core.handoff.models import HandoffEnvelope
from core.teams.models import TeamExecution


def project_identity(workspace: Path) -> str | None:
    """Return a stable repository identity without exposing embedded Git credentials."""
    git_config = workspace / ".git" / "config"
    if git_config.is_file():
        section = ""
        for raw in git_config.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("[") and line.endswith("]"):
                section = line
                continue
            if section == '[remote "origin"]' and line.startswith("url = "):
                return _sanitize_git_url(line[6:].strip())
    head = workspace / ".git" / "HEAD"
    if head.is_file():
        value = head.read_text(encoding="utf-8").strip()
        if value.startswith("ref: "):
            ref = workspace / ".git" / value[5:]
            if ref.is_file():
                return ref.read_text(encoding="utf-8").strip() or None
        return value or None
    return None


def _sanitize_git_url(value: str) -> str:
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlsplit(value)
        return urlunsplit((parsed.scheme, parsed.hostname or "", parsed.path, "", ""))
    if "@" in value and ":" in value.split("@", 1)[0]:
        return value.split("@", 1)[1]
    return value


def _result_summary(result: object) -> dict[str, Any]:
    if not isinstance(result, AgentResult):
        return {"type": type(result).__name__}
    return {
        "id": result.id,
        "agent": result.agent,
        "status": result.status,
        "summary": result.summary,
        "evidence_ids": list(result.evidence_ids),
        "handoff": result.handoff,
        "completed_at": result.completed_at.isoformat(),
    }


def create_handoff(
    execution: TeamExecution,
    *,
    source_environment: str,
    target_environment: str,
    workspace: Path | None = None,
) -> HandoffEnvelope:
    workspace = workspace or Path.cwd()
    context = dict(execution.context)
    objective = context.get("objective")
    objective_text = objective if isinstance(objective, str) else None
    results = {task_id: _result_summary(result) for task_id, result in execution.results.items()}
    evidence = []
    for result in execution.results.values():
        if isinstance(result, AgentResult):
            evidence.extend(result.evidence_ids)
    return HandoffEnvelope(
        source_environment=source_environment,
        source_workspace=str(workspace),
        target_environment=target_environment,
        project_id=project_identity(workspace),
        team_id=execution.team_id,
        execution_id=execution.execution_id,
        session_id=context.get("session_id") if isinstance(context.get("session_id"), str) else None,
        objective=objective_text,
        task_status={key: value.value for key, value in execution.task_status.items()},
        attempts=dict(execution.attempts),
        context=context,
        results=results,
        checkpoints=tuple(execution.checkpoints),
        evidence_ids=tuple(dict.fromkeys(evidence)),
        created_at=datetime.now(UTC).isoformat(),
    )


def validate_project(envelope: HandoffEnvelope, workspace: Path) -> None:
    current = project_identity(workspace)
    if envelope.project_id is not None and current is not None and envelope.project_id != current:
        raise ValueError("handoff project identity does not match the target workspace")


def resume_context(envelope: HandoffEnvelope, workspace: Path | None = None) -> dict[str, Any]:
    if workspace is not None:
        validate_project(envelope, workspace)
    context = dict(envelope.context)
    context["handoff_id"] = envelope.handoff_id
    context["handoff_source_environment"] = envelope.source_environment
    context["handoff_target_environment"] = envelope.target_environment
    context["handoff_execution_id"] = envelope.execution_id
    context["handoff_evidence_ids"] = list(envelope.evidence_ids)
    return context
