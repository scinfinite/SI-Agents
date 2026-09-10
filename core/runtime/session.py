"""Project-isolated runtime sessions."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


@dataclass(frozen=True)
class RuntimeSession:
    session_id: str
    project_id: str
    harness_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.session_id.strip() or not self.project_id.strip() or not self.harness_id.strip():
            raise ValueError("session requires identifiers")

    def close(self) -> "RuntimeSession":
        return RuntimeSession(self.session_id, self.project_id, self.harness_id, SessionStatus.CLOSED, self.created_at)


class SessionRegistry:
    def __init__(self) -> None:
        self._sessions: dict[str, RuntimeSession] = {}

    def create(self, session: RuntimeSession) -> RuntimeSession:
        if session.session_id in self._sessions:
            raise ValueError("duplicate session_id")
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> RuntimeSession | None:
        return self._sessions.get(session_id)

    def close(self, session_id: str) -> RuntimeSession:
        current = self._sessions.get(session_id)
        if current is None:
            raise KeyError(session_id)
        closed = current.close()
        self._sessions[session_id] = closed
        return closed
