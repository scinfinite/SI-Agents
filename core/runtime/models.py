"""Portable runtime and harness data contracts."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from core.governance.models import GovernanceRequest


class RuntimeKind(str, Enum):
    CLI = "cli"
    API = "api"
    IDE = "ide"
    AGENT = "agent"
    EMBEDDED = "embedded"


class InvocationStatus(str, Enum):
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RuntimeEventType(str, Enum):
    STARTED = "started"
    DELTA = "delta"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RuntimeErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    NOT_SUPPORTED = "not_supported"
    GOVERNANCE_DENIED = "governance_denied"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    EXECUTION_FAILED = "execution_failed"
    SESSION_NOT_FOUND = "session_not_found"


@dataclass(frozen=True)
class RuntimeCapabilities:
    streaming: bool = False
    cancellation: bool = False
    tool_calls: bool = False
    structured_output: bool = False
    session_continuity: bool = False


@dataclass(frozen=True)
class RuntimeEvent:
    type: RuntimeEventType
    request_id: str
    sequence: int
    data: object = None
    emitted_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.request_id.strip() or self.sequence < 0:
            raise ValueError("event requires request_id and non-negative sequence")
        if self.emitted_at.tzinfo is None:
            raise ValueError("event timestamp must be timezone-aware")


@dataclass(frozen=True)
class RuntimeError:
    code: RuntimeErrorCode
    message: str
    retryable: bool = False

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("runtime error message must not be empty")


@dataclass(frozen=True)
class InvocationRequest:
    capability_id: str
    input: object
    project_id: str
    session_id: str | None = None
    request_id: str = field(default_factory=lambda: str(uuid4()))
    metadata: tuple[tuple[str, str], ...] = ()
    governance: GovernanceRequest | None = None
    timeout_seconds: float | None = None
    streaming: bool = False

    def __post_init__(self) -> None:
        if not self.capability_id.strip() or not self.project_id.strip():
            raise ValueError("capability_id and project_id are required")
        if not self.request_id.strip():
            raise ValueError("request_id must not be empty")
        if self.session_id is not None and not self.session_id.strip():
            raise ValueError("session_id must not be empty when supplied")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if any(not key.strip() for key, _ in self.metadata):
            raise ValueError("metadata keys must not be empty")
        if len({key for key, _ in self.metadata}) != len(self.metadata):
            raise ValueError("metadata keys must be unique")


@dataclass(frozen=True)
class InvocationResponse:
    request_id: str
    status: InvocationStatus
    output: object = None
    events: tuple[RuntimeEvent, ...] = ()
    error: RuntimeError | None = None
    usage: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("response requires request_id")
        if self.status == InvocationStatus.FAILED and self.error is None:
            raise ValueError("failed response requires an error")
        if self.status != InvocationStatus.FAILED and self.error is not None:
            raise ValueError("only failed responses may carry an error")
        sequences = [event.sequence for event in self.events]
        if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
            raise ValueError("events must have unique, ordered sequence numbers")
        if any(event.request_id != self.request_id for event in self.events):
            raise ValueError("all events must belong to the response request")
        if any(not key.strip() or value < 0 for key, value in self.usage):
            raise ValueError("usage keys must be non-empty and values non-negative")
        if len({key for key, _ in self.usage}) != len(self.usage):
            raise ValueError("usage keys must be unique")
