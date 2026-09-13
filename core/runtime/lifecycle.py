"""Thread-safe lifecycle and idempotency authority for runtime invocations."""

from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock

from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeEvent,
    RuntimeEventType,
)


@dataclass(frozen=True)
class LifecycleEntry:
    request: InvocationRequest
    status: InvocationStatus
    response: InvocationResponse | None = None


class InvocationLedger:
    """Bounded, in-process request ledger used to enforce lifecycle invariants.

    The ledger is deliberately keyed by harness and request ID so a request ID cannot
    accidentally cross a harness boundary. Terminal responses are cached for bounded
    idempotent replay; active requests cannot be executed twice concurrently.
    """

    def __init__(self, *, max_entries: int = 4096) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self._max_entries = max_entries
        self._entries: OrderedDict[tuple[str, str], LifecycleEntry] = OrderedDict()
        self._lock = RLock()

    def begin(self, harness_id: str, request: InvocationRequest) -> InvocationResponse | None:
        """Reserve a request or return its cached terminal response.

        A reused request ID with a different immutable request payload is rejected to
        prevent an idempotency key from becoming a capability-confusion primitive.
        """
        key = self._key(harness_id, request.request_id)
        with self._lock:
            current = self._entries.get(key)
            if current is not None:
                self._entries.move_to_end(key)
                if current.request != request:
                    raise ValueError("request_id is already bound to a different request")
                if current.response is not None:
                    return current.response
                raise RuntimeError("request is already in progress")
            self._entries[key] = LifecycleEntry(request, InvocationStatus.ACCEPTED)
            self._trim()
            return None

    def finish(self, harness_id: str, request: InvocationRequest, response: InvocationResponse) -> InvocationResponse:
        """Commit the terminal response for a previously accepted request."""
        key = self._key(harness_id, request.request_id)
        with self._lock:
            current = self._entries.get(key)
            if current is None:
                raise KeyError(request.request_id)
            if current.request != request:
                raise ValueError("request_id is already bound to a different request")
            if current.response is not None:
                return current.response
            self._entries[key] = LifecycleEntry(request, response.status, response)
            self._entries.move_to_end(key)
            self._trim()
            return response

    def cancel(self, harness_id: str, request_id: str) -> bool:
        """Mark a known active request cancelled; terminal requests cannot change."""
        if not request_id.strip():
            return False
        key = self._key(harness_id, request_id)
        with self._lock:
            current = self._entries.get(key)
            if current is None or current.response is not None:
                return False
            response = InvocationResponse(
                request_id,
                InvocationStatus.CANCELLED,
                events=(RuntimeEvent(RuntimeEventType.CANCELLED, request_id, 0),),
            )
            self._entries[key] = LifecycleEntry(request, InvocationStatus.CANCELLED, response)
            self._entries.move_to_end(key)
            return True

    def is_cancelled(self, harness_id: str, request_id: str) -> bool:
        with self._lock:
            entry = self._entries.get(self._key(harness_id, request_id))
            return bool(entry and entry.status is InvocationStatus.CANCELLED)

    def get(self, harness_id: str, request_id: str) -> LifecycleEntry | None:
        key = self._key(harness_id, request_id)
        with self._lock:
            entry = self._entries.get(key)
            if entry is not None:
                self._entries.move_to_end(key)
            return entry

    @staticmethod
    def _key(harness_id: str, request_id: str) -> tuple[str, str]:
        if not harness_id.strip() or not request_id.strip():
            raise ValueError("harness_id and request_id must not be empty")
        return harness_id, request_id

    def _trim(self) -> None:
        while len(self._entries) > self._max_entries:
            self._entries.popitem(last=False)
