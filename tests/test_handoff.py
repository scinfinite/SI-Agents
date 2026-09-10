from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.base import AgentResult
from core.handoff.models import HandoffEnvelope, HandoffStatus
from core.handoff.service import create_handoff, project_identity, resume_context
from core.handoff.store import HandoffStore
from core.teams.models import TaskStatus, TeamExecution


def _execution() -> TeamExecution:
    execution = TeamExecution(team_id="engineering-repair", context={"objective": "repair it", "safe": True})
    execution.task_status = {"debug": TaskStatus.SUCCEEDED}
    execution.attempts = {"debug": 1}
    execution.results = {
        "debug": AgentResult(agent="debugger", status="succeeded", summary="diagnosed", evidence_ids=("ev-1",), handoff={"verified": True})
    }
    execution.checkpoints = ["diagnosis"]
    return execution


def test_handoff_round_trip_preserves_evidence(tmp_path: Path) -> None:
    envelope = create_handoff(_execution(), source_environment="termux", target_environment="codespace", workspace=tmp_path)
    store = HandoffStore(tmp_path / "handoffs")
    path = store.save(envelope)
    loaded = store.load(path)
    assert loaded.status is HandoffStatus.VALID
    assert loaded.team_id == "engineering-repair"
    assert loaded.evidence_ids == ("ev-1",)
    assert loaded.digest() == envelope.digest()
    assert path.stat().st_mode & 0o777 == 0o600


def test_handoff_rejects_tampering(tmp_path: Path) -> None:
    envelope = create_handoff(_execution(), source_environment="termux", target_environment="codespace", workspace=tmp_path)
    path = HandoffStore(tmp_path / "handoffs").save(envelope)
    payload = json.loads(path.read_text())
    payload["objective"] = "tampered"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="integrity"):
        HandoffStore(tmp_path / "handoffs").load(path)


def test_handoff_rejects_secret_like_context() -> None:
    with pytest.raises(ValueError, match="secret-like"):
        HandoffEnvelope(source_environment="termux", target_environment="codespace", context={"api_key": "x"})


def test_import_requires_target_environment(tmp_path: Path) -> None:
    envelope = create_handoff(_execution(), source_environment="termux", target_environment="codespace", workspace=tmp_path)
    path = HandoffStore(tmp_path / "handoffs").save(envelope)
    imported = HandoffStore().import_file(path, target_environment="codespace")
    assert imported.status is HandoffStatus.IMPORTED
    with pytest.raises(ValueError, match="targets"):
        HandoffStore().import_file(path, target_environment="termux")


def test_resume_context_adds_handoff_metadata(tmp_path: Path) -> None:
    envelope = create_handoff(_execution(), source_environment="termux", target_environment="codespace", workspace=tmp_path)
    context = resume_context(envelope)
    assert context["objective"] == "repair it"
    assert context["handoff_id"] == envelope.handoff_id
    assert context["handoff_evidence_ids"] == ["ev-1"]


def test_project_identity_sanitizes_embedded_credentials(tmp_path: Path) -> None:
    git = tmp_path / ".git"
    git.mkdir()
    (git / "config").write_text('[remote "origin"]\n\turl = https://user:secret@example.com/org/repo.git\n')
    assert project_identity(tmp_path) == "https://example.com/org/repo.git"


def test_project_identity_matches_different_git_commits(tmp_path: Path) -> None:
    git = tmp_path / ".git"
    git.mkdir()
    (git / "config").write_text('[remote "origin"]\n\turl = git@github.com:org/repo.git\n')
    assert project_identity(tmp_path) == "github.com:org/repo.git"


def test_handoff_rejects_same_environment() -> None:
    with pytest.raises(ValueError, match="differ"):
        HandoffEnvelope(source_environment="termux", target_environment="termux")
