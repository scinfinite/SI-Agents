"""Dependency-free HTTP transport for the versioned Control API and SDK streams."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from core.evidence.service import EvidenceService

from .openapi import document
from .pagination import filter_items, paginate
from .service import ControlApiService
from .subscriptions import SubscriptionRegistry


class ControlApiHandler(BaseHTTPRequestHandler):
    server_version = "SI-Agents-Control-API/1"
    protocol_version = "HTTP/1.1"

    @property
    def service(self) -> ControlApiService:
        return self.server.control_service  # type: ignore[attr-defined]

    @property
    def evidence(self) -> EvidenceService:
        return self.server.evidence_service  # type: ignore[attr-defined]

    @property
    def subscriptions(self) -> SubscriptionRegistry:
        return self.server.subscription_registry  # type: ignore[attr-defined]

    @property
    def api_token(self) -> str | None:
        return self.server.api_token  # type: ignore[attr-defined]

    @property
    def idempotency(self) -> dict[str, object]:
        return self.server.idempotency_cache  # type: ignore[attr-defined]

    def _request_id(self) -> str:
        value = self.headers.get("X-Request-ID", "").strip()
        return value[:128] if value else "api-request"

    def _send(self, status: int, payload: object) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Request-ID", self._request_id())
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def _authorize(self, path: str) -> None:
        if not self.api_token or path in {"/", "/api/v1", "/api/v1/health", "/api/v1/openapi.json"}:
            return
        value = self.headers.get("Authorization", "")
        if value != f"Bearer {self.api_token}":
            raise PermissionError("valid bearer authentication is required")

    def _read_json(self) -> dict[str, object]:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ValueError("Content-Length is required")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length < 0 or length > 1_048_576:
            raise ValueError("request body exceeds 1 MiB limit")
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("request body must be valid UTF-8 JSON") from exc
        if not isinstance(payload, dict):
            raise TypeError("request body must be a JSON object")
        return payload

    def _identity(self) -> tuple[str, str]:
        subject_id = self.headers.get("X-SI-Subject", "").strip()
        project_id = self.headers.get("X-SI-Project", "").strip()
        if not subject_id or not project_id:
            raise PermissionError("X-SI-Subject and X-SI-Project are required")
        return subject_id[:512], project_id[:512]

    def _collection(self, values: list[dict[str, object]], parsed) -> object:
        params = parse_qs(parsed.query)
        if not any(key in params for key in ("limit", "cursor", "q")) and not any(key.startswith("filter.") for key in params):
            return values
        try:
            limit = int(params.get("limit", ["100"])[0])
        except ValueError as exc:
            raise ValueError("limit must be an integer") from exc
        query = params.get("q", [None])[0]
        filters = {key.removeprefix("filter."): value[0] for key, value in params.items() if key.startswith("filter.") and value}
        public_params = {"q": query or "", **{f"filter.{k}": v for k, v in sorted(filters.items())}}
        selected = filter_items(values, query, filters)
        return paginate(selected, limit=limit, cursor=params.get("cursor", [None])[0], params=public_params)

    def _event_payload(self, index: int, event: dict[str, object]) -> str:
        return f"id: {index}\nevent: {event.get('event_type', 'message')}\ndata: {json.dumps(event, sort_keys=True, separators=(',', ':'))}\n\n"

    def _sse(self, after: int) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Request-ID", self._request_id())
        self.end_headers()
        self.close_connection = True
        deadline = time.monotonic() + 15.0
        index = max(0, after)
        try:
            while time.monotonic() < deadline:
                events = self.service.events()
                while index < len(events):
                    payload = self._event_payload(index, events[index])
                    self.wfile.write(payload.encode())
                    self.wfile.flush()
                    index += 1
                self.wfile.write(b": heartbeat\n\n")
                self.wfile.flush()
                time.sleep(0.25)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return

    def _websocket(self) -> None:
        key = self.headers.get("Sec-WebSocket-Key")
        if not key or self.headers.get("Upgrade", "").lower() != "websocket":
            self._send(426, {"error": "upgrade_required", "message": "WebSocket upgrade is required", "request_id": self._request_id()})
            return
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        self.close_connection = True
        try:
            for event in self.service.events():
                data = json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
                if len(data) >= 126:
                    continue
                self.connection.sendall(b"\x81" + bytes([len(data)]) + data)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            self._authorize(path)
            if path == "/api/v1/events/stream":
                after = int(parse_qs(parsed.query).get("after", ["0"])[0])
                if after < 0 or after > 1_000_000:
                    raise ValueError("after must be a bounded non-negative integer")
                self._sse(after)
                return
            if path == "/api/v1/events/ws":
                self._websocket()
                return
            routes: dict[str, object] = {
                "/": self.service.snapshot().as_dict(),
                "/api/v1": self.service.snapshot().as_dict(),
                "/api/v1/health": {"status": "ok", "api_version": "v1"},
                "/api/v1/openapi.json": document(),
                "/api/v1/agents": self.service.agents(),
                "/api/v1/teams": self.service.teams(),
                "/api/v1/workflows": self.service.workflows(),
                "/api/v1/organization": self.service.organization(),
                "/api/v1/skills": self.service.skills(),
                "/api/v1/memory": self.service.memory(),
                "/api/v1/governance": self.service.governance_state(),
                "/api/v1/evidence": self.service.evidence(),
                "/api/v1/evidence/records": self.evidence.list(),
                "/api/v1/environments": self.service.environments(),
                "/api/v1/harnesses": self.service.harnesses(),
                "/api/v1/settings": self.service.settings(),
                "/api/v1/visualization": self.service.visualization(),
                "/api/v1/events": self.service.events(),
                "/api/v1/runs": self.service.runs(),
            }
            if path == "/api/v1/subscriptions":
                self._send(200, [self.subscriptions.public(item) for item in self.subscriptions.list()])
                return
            if path == "/api/v1/approvals":
                subject_id, project_id = self._identity()
                params = parse_qs(parsed.query)
                limit = int(params.get("limit", ["100"])[0])
                self._send(200, self.service.approvals_queue(subject_id=subject_id, project_id=project_id, limit=limit))
                return
            if path in routes:
                self._send(200, self._collection(routes[path], parsed) if isinstance(routes[path], list) else routes[path])
                return
            if path.startswith("/api/v1/approvals/"):
                approval_id = path.removeprefix("/api/v1/approvals/")
                subject_id, project_id = self._identity()
                if approval_id.endswith("/events"):
                    self._send(200, self.service.approval_events(approval_id.removesuffix("/events"), subject_id=subject_id, project_id=project_id))
                else:
                    self._send(200, self.service.get_approval(approval_id, subject_id=subject_id, project_id=project_id))
                return
            if path.startswith("/api/v1/evidence/"):
                evidence_id = path.removeprefix("/api/v1/evidence/")
                if evidence_id.endswith("/verify"):
                    self._send(404, {"error": "not_found", "message": "route not found", "request_id": self._request_id()})
                    return
                self._send(200, self.evidence.get(evidence_id))
                return
            if path.startswith("/api/v1/runs/"):
                suffix = path.removeprefix("/api/v1/runs/")
                if suffix.endswith("/timeline"):
                    self._send(200, self.evidence.timeline(suffix.removesuffix("/timeline")))
                    return
                self._send(200, self.service.get_run(suffix))
                return
        except PermissionError as exc:
            self._send(403, {"error": "forbidden", "message": str(exc), "request_id": self._request_id()})
            return
        except (TypeError, ValueError, KeyError) as exc:
            self._send(400 if not isinstance(exc, KeyError) else 404, {"error": "invalid_request" if not isinstance(exc, KeyError) else "not_found", "message": str(exc), "request_id": self._request_id()})
            return
        self._send(404, {"error": "not_found", "message": "route not found", "request_id": self._request_id()})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        try:
            self._authorize(path)
            payload = self._read_json()
            if path == "/api/v1/runs":
                key = self.headers.get("X-Idempotency-Key", "").strip()
                if key:
                    if len(key) > 256:
                        raise ValueError("idempotency key is too long")
                    scope = self.headers.get("Authorization", "") + "|" + self.headers.get("X-SI-Subject", "") + "|" + self.headers.get("X-SI-Project", "")
                    cache_key = hashlib.sha256((scope + "|" + key).encode()).hexdigest()
                    if cache_key in self.idempotency:
                        self._send(200, self.idempotency[cache_key])
                        return
                result = self.service.create_run(payload)
                if key:
                    self.idempotency[cache_key] = result
                    if len(self.idempotency) > 1024:
                        self.idempotency.pop(next(iter(self.idempotency)))
                self._send(202, result)
                return
            if path == "/api/v1/subscriptions":
                event_types = payload.get("event_types", [])
                if not isinstance(event_types, list):
                    raise ValueError("event_types must be a list")
                item = self.subscriptions.create(event_types=event_types, subject=payload.get("subject") if isinstance(payload.get("subject"), str) else None, transport=str(payload.get("transport", "sse")), target=payload.get("target") if isinstance(payload.get("target"), str) else None)
                result = self.subscriptions.public(item)
                if item.secret:
                    result["secret"] = item.secret
                self._send(201, result)
                return
            if path == "/api/v1/approvals":
                result = self.service.create_approval(payload)
                self._send(201, result)
                return
            if path.startswith("/api/v1/approvals/") and path.endswith("/decide"):
                approval_id = path.removeprefix("/api/v1/approvals/").removesuffix("/decide")
                result = self.service.decide_approval(approval_id, payload)
                self._send(200, result)
                return
            if path == "/api/v1/evidence":
                result = self.evidence.record(payload)
                self._send(201, result)
                return
            if path.startswith("/api/v1/evidence/") and path.endswith("/verify"):
                evidence_id = path.removeprefix("/api/v1/evidence/").removesuffix("/verify")
                state = payload.get("verification")
                if not isinstance(state, str):
                    raise ValueError("verification is required")
                self._send(200, self.evidence.verify(evidence_id, state))
                return
        except PermissionError as exc:
            self._send(403, {"error": "governance_denied", "message": str(exc), "request_id": self._request_id()})
            return
        except KeyError:
            self._send(404, {"error": "not_found", "message": "resource not found", "request_id": self._request_id()})
            return
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send(400, {"error": "invalid_request", "message": str(exc), "request_id": self._request_id()})
            return
        self._send(404, {"error": "not_found", "message": "route not found", "request_id": self._request_id()})

    def do_DELETE(self):
        path = urlparse(self.path).path.rstrip("/")
        try:
            self._authorize(path)
            if path.startswith("/api/v1/subscriptions/"):
                self.subscriptions.delete(path.removeprefix("/api/v1/subscriptions/"))
                self._send(204, None)
                return
        except PermissionError as exc:
            self._send(403, {"error": "forbidden", "message": str(exc), "request_id": self._request_id()})
            return
        except KeyError:
            self._send(404, {"error": "not_found", "message": "subscription not found", "request_id": self._request_id()})
            return
        self._send(404, {"error": "not_found", "message": "route not found", "request_id": self._request_id()})

    def log_message(self, format, *args):
        return


def create_server(service: ControlApiService, host: str = "127.0.0.1", port: int = 8787, *, auth_token: str | None = None) -> ThreadingHTTPServer:
    """Create a localhost-first server; remote exposure remains explicit and authenticated."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Control API is localhost-only; explicit remote exposure is not supported by this transport")
    server = ThreadingHTTPServer((host, port), ControlApiHandler)
    server.control_service = service  # type: ignore[attr-defined]
    server.evidence_service = EvidenceService(str(Path(service.root) / ".si" / "evidence.v1.json"))  # type: ignore[attr-defined]
    server.subscription_registry = SubscriptionRegistry()  # type: ignore[attr-defined]
    server.idempotency_cache = {}  # type: ignore[attr-defined]
    server.api_token = auth_token if auth_token is not None else os.environ.get("SI_API_TOKEN")  # type: ignore[attr-defined]
    return server
