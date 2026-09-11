"""Phase 47 OpenCode server bridge.

OpenCode is treated as a downstream protocol adapter. This module translates
its HTTP/SSE surface into SI runtime contracts without importing OpenCode
permissions, provenance, or authority into the SI control plane.
"""
from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.parse
import urllib.request
from builtins import RuntimeError as BuiltinRuntimeError
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

from core.runtime.models import InvocationRequest, InvocationResponse, InvocationStatus, RuntimeCapabilities, RuntimeError as SIRuntimeError, RuntimeErrorCode, RuntimeEvent, RuntimeEventType, RuntimeKind
from core.runtime.protocol import HarnessAdapter, HarnessMetadata


class OpenCodeTransport(Protocol):
    def request(self, method: str, path: str, *, query: Mapping[str, str] | None = None, body: Mapping[str, Any] | None = None) -> Any: ...
    def stream(self, path: str, *, query: Mapping[str, str] | None = None) -> Iterable[Mapping[str, Any]]: ...


class OpenCodeTransportError(BuiltinRuntimeError):
    def __init__(self, status: int | None, kind: str) -> None:
        self.status = status
        self.kind = kind
        super().__init__(kind)


class UrllibOpenCodeTransport:
    """Minimal stdlib transport; callers can inject a test or platform transport."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _url(self, path: str, query: Mapping[str, str] | None = None) -> str:
        url = f"{self.base_url}/{path.lstrip('/')}"
        return f"{url}?{urllib.parse.urlencode(query)}" if query else url

    def request(self, method: str, path: str, *, query: Mapping[str, str] | None = None, body: Mapping[str, Any] | None = None) -> Any:
        payload = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(self._url(path, query), data=payload, method=method.upper(), headers={"Accept": "application/json", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise OpenCodeTransportError(exc.code, "http_error") from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            raise OpenCodeTransportError(None, "transport_error") from exc
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OpenCodeTransportError(None, "invalid_json") from exc

    def stream(self, path: str, *, query: Mapping[str, str] | None = None) -> Iterator[Mapping[str, Any]]:
        request = urllib.request.Request(self._url(path, query), method="GET", headers={"Accept": "text/event-stream"})
        try:
            response = urllib.request.urlopen(request, timeout=self.timeout)
        except urllib.error.HTTPError as exc:
            raise OpenCodeTransportError(exc.code, "http_error") from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            raise OpenCodeTransportError(None, "transport_error") from exc
        with response:
            data: list[str] = []
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                if line.startswith("data:"):
                    data.append(line[5:].lstrip())
                elif not line and data:
                    payload = "\n".join(data)
                    data.clear()
                    try:
                        parsed = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(parsed, dict):
                        yield parsed


@dataclass(frozen=True)
class OpenCodeSession:
    session_id: str
    project_id: str


class OpenCodeBridge(HarnessAdapter):
    """Translate OpenCode HTTP/SSE into the SI HarnessAdapter contract."""

    def __init__(self, base_url: str = "http://127.0.0.1:4096", *, version: str = "unknown", transport: OpenCodeTransport | None = None, timeout: float = 30.0, allow_remote: bool = False) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OpenCode base_url must be an absolute HTTP(S) URL")
        if not allow_remote and not self._is_loopback(parsed.hostname):
            raise ValueError("remote OpenCode endpoints require allow_remote=True")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.base_url = base_url.rstrip("/")
        self._transport = transport or UrllibOpenCodeTransport(self.base_url, timeout)
        self._metadata = HarnessMetadata("opencode", RuntimeKind.AGENT, version)
        self._capabilities = RuntimeCapabilities(streaming=True, cancellation=True, tool_calls=True, structured_output=True, session_continuity=True)
        self._sessions: dict[str, str] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _is_loopback(hostname: str | None) -> bool:
        if not hostname:
            return False
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            return True
        try:
            return hostname == socket.gethostbyname("localhost")
        except OSError:
            return False

    @property
    def metadata(self) -> HarnessMetadata:
        return self._metadata

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return self._capabilities

    def health(self) -> Mapping[str, Any]:
        result = self._request("GET", "/global/health")
        if not isinstance(result, Mapping) or result.get("healthy") is not True:
            raise BuiltinRuntimeError("OpenCode health check failed")
        return result

    def create_session(self, project_id: str) -> OpenCodeSession:
        if not project_id.strip():
            raise ValueError("project_id is required")
        result = self._request("POST", "/session", query={"directory": project_id}, body={})
        session_id = self._session_id(result)
        return OpenCodeSession(session_id, project_id)

    def invoke(self, request: InvocationRequest) -> InvocationResponse:
        session_id: str | None = None
        try:
            session_id = request.session_id or self.create_session(request.project_id).session_id
            with self._lock:
                self._sessions[request.request_id] = session_id
            body = self._message_body(request)
            if request.streaming:
                self._request("POST", f"/session/{urllib.parse.quote(session_id, safe='')}/prompt_async", body=body)
                return self._invoke_streaming(request, session_id)
            result = self._request("POST", f"/session/{urllib.parse.quote(session_id, safe='')}/message", body=body)
            output = self._extract_text(result)
            event = RuntimeEvent(RuntimeEventType.COMPLETED, request.request_id, 0, output)
            return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output=output, events=(event,))
        except OpenCodeTransportError as exc:
            error = SIRuntimeError(RuntimeErrorCode.TIMEOUT if exc.kind == "transport_error" else RuntimeErrorCode.EXECUTION_FAILED, "OpenCode transport request failed", retryable=exc.status in {408, 429, 500, 502, 503, 504})
            return InvocationResponse(request.request_id, InvocationStatus.FAILED, error=error)
        finally:
            with self._lock:
                self._sessions.pop(request.request_id, None)

    def cancel(self, request_id: str) -> bool:
        with self._lock:
            session_id = self._sessions.get(request_id, request_id)
        try:
            result = self._request("POST", f"/session/{urllib.parse.quote(session_id, safe='')}/abort")
        except OpenCodeTransportError:
            return False
        return result is True or (isinstance(result, Mapping) and result.get("aborted") is True)

    def event_stream(self, session_id: str) -> Iterator[Mapping[str, Any]]:
        for event in self._transport.stream("/event"):
            if self._event_session_id(event) == session_id:
                yield event

    def _invoke_streaming(self, request: InvocationRequest, session_id: str) -> InvocationResponse:
        events: list[RuntimeEvent] = []
        chunks: list[str] = []
        sequence = 0
        for raw in self.event_stream(session_id):
            event_type = str(raw.get("type", ""))
            if event_type in {"message.part.updated", "message.part.delta"}:
                text = self._event_text(raw)
                if text:
                    chunks.append(text)
                    events.append(RuntimeEvent(RuntimeEventType.DELTA, request.request_id, sequence, text))
                    sequence += 1
            if event_type == "session.error":
                events.append(RuntimeEvent(RuntimeEventType.FAILED, request.request_id, sequence, {"source": "opencode"}))
                return InvocationResponse(request.request_id, InvocationStatus.FAILED, output="".join(chunks), events=tuple(events), error=SIRuntimeError(RuntimeErrorCode.EXECUTION_FAILED, "OpenCode session failed", retryable=False))
            if event_type in {"session.idle", "session.completed"}:
                events.append(RuntimeEvent(RuntimeEventType.COMPLETED, request.request_id, sequence, "".join(chunks)))
                return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output="".join(chunks), events=tuple(events))
        return InvocationResponse(request.request_id, InvocationStatus.FAILED, output="".join(chunks), events=tuple(events), error=SIRuntimeError(RuntimeErrorCode.EXECUTION_FAILED, "OpenCode event stream ended before a terminal event"))

    @staticmethod
    def _session_id(result: Any) -> str:
        if isinstance(result, Mapping) and isinstance(result.get("id"), str) and result["id"].strip():
            return result["id"]
        raise BuiltinRuntimeError("OpenCode session response did not contain an id")

    @staticmethod
    def _message_body(request: InvocationRequest) -> dict[str, Any]:
        if isinstance(request.input, Mapping) and isinstance(request.input.get("parts"), list):
            parts = request.input["parts"]
        else:
            text = request.input if isinstance(request.input, str) else json.dumps(request.input, ensure_ascii=False, sort_keys=True)
            parts = [{"type": "text", "text": text}]
        body: dict[str, Any] = {"parts": parts}
        metadata = dict(request.metadata)
        if metadata.get("provider_id") and metadata.get("model_id"):
            body["model"] = {"providerID": metadata["provider_id"], "modelID": metadata["model_id"]}
        for key in ("agent", "system", "variant", "tools", "format"):
            if key in metadata:
                body[key] = metadata[key]
        return body

    @staticmethod
    def _extract_text(result: Any) -> str:
        if not isinstance(result, Mapping):
            return ""
        parts = result.get("parts", [])
        if not isinstance(parts, list):
            return ""
        text: list[str] = []
        for part in parts:
            if isinstance(part, Mapping) and part.get("type") == "text" and isinstance(part.get("text"), str):
                text.append(part["text"])
        return "".join(text)

    @staticmethod
    def _event_session_id(event: Mapping[str, Any]) -> str | None:
        properties = event.get("properties")
        if isinstance(properties, Mapping):
            for key in ("sessionID", "sessionId", "session_id"):
                value = properties.get(key)
                if isinstance(value, str):
                    return value
            part = properties.get("part")
            if isinstance(part, Mapping) and isinstance(part.get("sessionID"), str):
                return part["sessionID"]
        return event.get("sessionID") if isinstance(event.get("sessionID"), str) else None

    @staticmethod
    def _event_text(event: Mapping[str, Any]) -> str:
        properties = event.get("properties")
        candidates = [properties]
        if isinstance(properties, Mapping):
            candidates.append(properties.get("part"))
        for candidate in candidates:
            if isinstance(candidate, Mapping):
                for key in ("delta", "text"):
                    value = candidate.get(key)
                    if isinstance(value, str):
                        return value
        return ""

    def _request(self, method: str, path: str, *, query: Mapping[str, str] | None = None, body: Mapping[str, Any] | None = None) -> Any:
        return self._transport.request(method, path, query=query, body=body)
