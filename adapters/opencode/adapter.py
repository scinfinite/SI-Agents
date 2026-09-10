"""OpenCode headless-server adapter.

The adapter talks to OpenCode's documented HTTP server API. Provider/model
credentials remain owned by OpenCode (or its configured gateway), not by
SI-Agents.
"""

import base64
import json
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeCapabilities,
    RuntimeError as RuntimeFailure,
    RuntimeErrorCode,
    RuntimeEvent,
    RuntimeEventType,
    RuntimeKind,
)
from core.runtime.protocol import HarnessAdapter, HarnessMetadata

from .config import OpenCodeConfig


@dataclass
class OpenCodeAdapter:
    config: OpenCodeConfig = field(default_factory=OpenCodeConfig)
    _sessions: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    @property
    def metadata(self) -> HarnessMetadata:
        return HarnessMetadata(harness_id="opencode", kind=RuntimeKind.AGENT, version="server-v1")

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            streaming=False,
            cancellation=True,
            tool_calls=True,
            structured_output=True,
            session_continuity=True,
        )

    def invoke(self, request: InvocationRequest) -> InvocationResponse:
        if request.streaming:
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.FAILED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.NOT_SUPPORTED,
                    message="OpenCode server adapter currently uses the synchronous message endpoint",
                    retryable=False,
                ),
            )
        try:
            session_id = request.session_id or self._create_session(request.project_id)
            with self._lock:
                self._sessions[request.request_id] = session_id
            result = self._post(f"/session/{session_id}/message", self._message_payload(request))
            output = self._extract_text(result)
            event = RuntimeEvent(
                type=RuntimeEventType.COMPLETED,
                request_id=request.request_id,
                sequence=0,
                data={"session_id": session_id},
            )
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.COMPLETED,
                output=output,
                events=(event,),
            )
        except _OpenCodeHTTPError as exc:
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.FAILED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.EXECUTION_FAILED,
                    message=f"OpenCode returned HTTP {exc.status}",
                    retryable=exc.status in {408, 409, 425, 429} or exc.status >= 500,
                ),
            )
        except (urllib.error.URLError, TimeoutError) as exc:
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.FAILED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.EXECUTION_FAILED,
                    message=f"OpenCode server unavailable: {exc}",
                    retryable=True,
                ),
            )
        except (json.JSONDecodeError, UnicodeDecodeError, OSError, ValueError) as exc:
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.FAILED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.EXECUTION_FAILED,
                    message=f"Invalid OpenCode response: {exc}",
                    retryable=False,
                ),
            )

    def cancel(self, request_id: str) -> bool:
        with self._lock:
            session_id = self._sessions.get(request_id)
        if session_id is None:
            # Accept a raw OpenCode session ID as a useful administrative fallback.
            session_id = request_id
        try:
            self._post(f"/session/{session_id}/abort", {})
            return True
        except (_OpenCodeHTTPError, urllib.error.URLError, TimeoutError, OSError):
            return False

    def _create_session(self, project_id: str) -> str:
        result = self._post("/session", {"title": f"SI-Agent:{project_id}"})
        session_id = result.get("id") if isinstance(result, dict) else None
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("OpenCode did not return a session id")
        return session_id

    @staticmethod
    def _message_payload(request: InvocationRequest) -> dict[str, Any]:
        content = request.input if isinstance(request.input, str) else json.dumps(request.input)
        metadata = dict(request.metadata)
        payload: dict[str, Any] = {"parts": [{"type": "text", "text": content}]}
        if metadata.get("model"):
            payload["model"] = metadata["model"]
        if metadata.get("agent"):
            payload["agent"] = metadata["agent"]
        return payload

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        parts = payload.get("parts", [])
        texts = [
            part.get("text", "")
            for part in parts
            if isinstance(part, dict) and part.get("type") == "text"
        ]
        return "".join(texts)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.password:
            token = base64.b64encode(f"{self.config.username}:{self.config.password}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        request = urllib.request.Request(
            self.config.base_url.rstrip("/") + path,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise _OpenCodeHTTPError(exc.code) from exc
        if not raw:
            return {}
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("OpenCode response must be a JSON object")
        return parsed


class _OpenCodeHTTPError(Exception):
    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"HTTP {status}")


assert isinstance(OpenCodeAdapter(), HarnessAdapter)
