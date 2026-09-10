"""Dependency-free HTTP transport for the versioned Control API."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .openapi import document
from .service import ControlApiService


class ControlApiHandler(BaseHTTPRequestHandler):
    server_version = "SI-Agents-Control-API/1"
    protocol_version = "HTTP/1.1"

    @property
    def service(self) -> ControlApiService:
        return self.server.control_service  # type: ignore[attr-defined]

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
        self.wfile.write(body)

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

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        routes: dict[str, object] = {
            "/": self.service.snapshot().as_dict(), "/api/v1": self.service.snapshot().as_dict(),
            "/api/v1/health": {"status": "ok", "api_version": "v1"},
            "/api/v1/openapi.json": document(), "/api/v1/agents": self.service.agents(),
            "/api/v1/teams": self.service.teams(), "/api/v1/workflows": self.service.workflows(),
            "/api/v1/organization": self.service.organization(), "/api/v1/skills": self.service.skills(),
            "/api/v1/memory": self.service.memory(), "/api/v1/governance": self.service.governance_state(),
            "/api/v1/events": self.service.events(), "/api/v1/runs": self.service.runs(),
        }
        if path in routes:
            self._send(200, routes[path])
            return
        if path.startswith("/api/v1/runs/"):
            run_id = path.removeprefix("/api/v1/runs/")
            try:
                self._send(200, self.service.get_run(run_id))
            except KeyError:
                self._send(404, {"error": "not_found", "message": "run not found", "request_id": self._request_id()})
            return
        self._send(404, {"error": "not_found", "message": "route not found", "request_id": self._request_id()})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        if path != "/api/v1/runs":
            self._send(404, {"error": "not_found", "message": "route not found", "request_id": self._request_id()})
            return
        try:
            payload = self._read_json()
            result = self.service.create_run(payload)
        except PermissionError as exc:
            self._send(403, {"error": "governance_denied", "message": str(exc), "request_id": self._request_id()})
            return
        except (TypeError, ValueError) as exc:
            self._send(400, {"error": "invalid_request", "message": str(exc), "request_id": self._request_id()})
            return
        self._send(202, result)

    def log_message(self, format, *args):
        return


def create_server(service: ControlApiService, host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    """Create a localhost-first server; callers own its lifecycle."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Control API is localhost-only; explicit remote exposure is not supported by this transport")
    server = ThreadingHTTPServer((host, port), ControlApiHandler)
    server.control_service = service  # type: ignore[attr-defined]
    return server
