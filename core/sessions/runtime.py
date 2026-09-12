"""Runtime-facing persistent session adapter.

The adapter preserves the existing runtime contract while moving session lifecycle storage
from the process-local registry into SI Core durable storage. It never restores authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from .store import PersistentSession, SessionOwner, SessionState, SessionStore


@dataclass
class PersistentSessionAdapter:
    store: SessionStore

    def create(self, *, session_id: str, subject_id: str, project_id: str, harness_id: str, workspace_id: str | None = None, expires_at: float | None = None) -> PersistentSession:
        return self.store.create(PersistentSession(session_id, SessionOwner(subject_id, project_id, workspace_id), harness_id, expires_at=expires_at))

    def require(self, session_id: str, *, subject_id: str, project_id: str, harness_id: str) -> PersistentSession:
        session = self.store.get(session_id, subject_id=subject_id, project_id=project_id)
        if session.harness_id != harness_id:
            raise PermissionError("session harness mismatch")
        if session.state not in {SessionState.ACTIVE, SessionState.PAUSED}:
            raise ValueError("session is not resumable")
        return session

    def close(self, session_id: str, *, subject_id: str, project_id: str) -> PersistentSession:
        return self.store.update_state(session_id, subject_id=subject_id, project_id=project_id, state=SessionState.CLOSED)

    def pause(self, session_id: str, *, subject_id: str, project_id: str, expected_revision: int | None = None) -> PersistentSession:
        return self.store.update_state(session_id, subject_id=subject_id, project_id=project_id, state=SessionState.PAUSED, expected_revision=expected_revision)

    def resume(self, session_id: str, *, subject_id: str, project_id: str, expected_revision: int | None = None) -> PersistentSession:
        return self.store.update_state(session_id, subject_id=subject_id, project_id=project_id, state=SessionState.ACTIVE, expected_revision=expected_revision)
