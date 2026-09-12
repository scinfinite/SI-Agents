import json

import pytest

from core.sessions import PersistentSession, PersistentSessionAdapter, SessionOwner, SessionState, SessionStore


def make_session(sid="s1", subject="user-1", project="project-1", harness="opencode", **kwargs):
    return PersistentSession(sid, SessionOwner(subject, project, kwargs.pop("workspace_id", None)), harness, **kwargs)


def test_durable_lifecycle_and_restart(tmp_path):
    db = tmp_path / "sessions.db"
    store = SessionStore(db)
    session = store.create(make_session("s1"), state={"task_ids": ["t1"], "agent_ids": ["a1"]})
    store.append_event("s1", subject_id="user-1", project_id="project-1", kind="task.started", payload={"task_id": "t1"})
    store.close()
    reopened = SessionStore(db)
    loaded = reopened.get("s1", subject_id="user-1", project_id="project-1")
    assert loaded.session_id == session.session_id
    assert reopened.read_state("s1", subject_id="user-1", project_id="project-1")["state"]["task_ids"] == ["t1"]
    assert reopened.events("s1", subject_id="user-1", project_id="project-1")[0].sequence == 1


def test_owner_and_project_isolation_is_fail_closed(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session())
    with pytest.raises(PermissionError):
        store.get("s1", subject_id="other", project_id="project-1")
    with pytest.raises(PermissionError):
        store.update_state("s1", subject_id="other", project_id="project-1", state=SessionState.PAUSED)


def test_revision_prevents_lost_updates(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session())
    current = store.update_state("s1", subject_id="user-1", project_id="project-1", state=SessionState.PAUSED, expected_revision=0)
    assert current.revision == 1
    with pytest.raises(ValueError, match="revision conflict"):
        store.update_state("s1", subject_id="user-1", project_id="project-1", state=SessionState.ACTIVE, expected_revision=0)


def test_events_are_ordered_and_paginated(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session())
    for kind in ("one", "two", "three"):
        store.append_event("s1", subject_id="user-1", project_id="project-1", kind=kind, payload={})
    assert [e.sequence for e in store.events("s1", subject_id="user-1", project_id="project-1", after=1, limit=2)] == [2, 3]
    assert [e.kind for e in store.replay("s1", subject_id="user-1", project_id="project-1")] == ["one", "two", "three"]


def test_secret_like_session_state_is_rejected(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    with pytest.raises(ValueError, match="secret-like"):
        store.create(make_session(), state={"api_key": "do-not-store"})
    store.create(make_session())
    with pytest.raises(ValueError, match="secret-like"):
        store.set_context("s1", subject_id="user-1", project_id="project-1", context={"nested": {"token": "x"}})


def test_export_import_is_schema_checked_and_owner_bound(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session(), state={"workflow_ids": ["w1"]})
    artifact = store.add_artifact("s1", subject_id="user-1", project_id="project-1", kind="evidence", name="proof", content=b"proof")
    bundle = store.export("s1", subject_id="user-1", project_id="project-1")
    assert bundle.schema_version == "si.session.v1"
    assert bundle.artifacts[0].digest == artifact.digest
    restored = store.import_session(bundle, subject_id="user-1", project_id="project-1", new_session_id="s2")
    assert restored.session_id == "s2"
    assert store.artifacts("s2", subject_id="user-1", project_id="project-1")[0].digest == artifact.digest
    with pytest.raises(PermissionError):
        store.import_session(bundle, subject_id="attacker", project_id="project-1", new_session_id="s3")
    tampered = type(bundle)("other.v1", bundle.session, bundle.state, bundle.events, bundle.artifacts)
    with pytest.raises(ValueError, match="schema"):
        store.import_session(tampered, subject_id="user-1", project_id="project-1")


def test_clone_creates_new_lineage_without_reusing_identity(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session(), state={"history": ["h1"]})
    clone = store.clone("s1", subject_id="user-1", project_id="project-1", branch_name="experiment", new_session_id="s2")
    assert clone.session_id == "s2"
    assert clone.parent_session_id == "s1"
    assert clone.branch_name == "experiment"
    assert clone.revision == 0
    assert store.read_state("s2", subject_id="user-1", project_id="project-1")["state"]["history"] == ["h1"]


def test_expiry_is_durable_and_archived_sessions_are_immutable(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session(expires_at=10.0))
    expired = store.expire_due(now=20.0)
    assert expired[0].state is SessionState.EXPIRED
    assert store.get("s1", subject_id="user-1", project_id="project-1").state is SessionState.EXPIRED
    store.create(make_session("s2"))
    archived = store.archive("s2", subject_id="user-1", project_id="project-1")
    assert archived.state is SessionState.ARCHIVED
    with pytest.raises(ValueError, match="archived"):
        store.update_state("s2", subject_id="user-1", project_id="project-1", state=SessionState.ACTIVE)


def test_artifact_digest_and_limits(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session())
    artifact = store.add_artifact("s1", subject_id="user-1", project_id="project-1", kind="log", name="run.txt", content=b"hello")
    assert len(artifact.digest) == 64
    assert store.artifacts("s1", subject_id="user-1", project_id="project-1")[0].digest == artifact.digest
    with pytest.raises(ValueError, match="safety limit"):
        store.add_artifact("s1", subject_id="user-1", project_id="project-1", kind="log", name="huge", content=b"x" * (256 * 1024 + 1))


def test_search_is_scoped_and_bounded(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session("s1"))
    store.create(make_session("s2", harness="cli"))
    store.append_event("s1", subject_id="user-1", project_id="project-1", kind="workflow.completed", payload={"name": "alpha"})
    assert [s.session_id for s in store.search(subject_id="user-1", project_id="project-1", text="alpha")] == ["s1"]
    with pytest.raises(ValueError):
        store.search(subject_id="user-1", project_id="project-1", text="x" * 257)


def test_session_state_is_json_safe(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    store.create(make_session())
    store.set_context("s1", subject_id="user-1", project_id="project-1", context={"usage": {"input_tokens": 12}}, token_usage={"cost": 0.02})
    state = store.read_state("s1", subject_id="user-1", project_id="project-1")
    json.dumps(state)
    assert state["token_cost"]["cost"] == 0.02


def test_persistent_runtime_adapter_enforces_harness_and_continuity(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")
    adapter = PersistentSessionAdapter(store)
    adapter.create(session_id="s1", subject_id="user-1", project_id="project-1", harness_id="opencode")
    assert adapter.require("s1", subject_id="user-1", project_id="project-1", harness_id="opencode").state is SessionState.ACTIVE
    with pytest.raises(PermissionError):
        adapter.require("s1", subject_id="user-1", project_id="project-1", harness_id="cli")
    paused = adapter.pause("s1", subject_id="user-1", project_id="project-1", expected_revision=0)
    assert paused.state is SessionState.PAUSED
    assert adapter.require("s1", subject_id="user-1", project_id="project-1", harness_id="opencode").state is SessionState.PAUSED
    resumed = adapter.resume("s1", subject_id="user-1", project_id="project-1", expected_revision=1)
    assert resumed.state is SessionState.ACTIVE
