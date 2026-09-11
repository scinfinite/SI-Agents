# ruff: noqa: E701, E702
"""Dependency-free localhost-first Web server over the Control API."""

from __future__ import annotations

import json
import secrets
import signal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Event, Thread
from urllib.parse import urlparse

from core.agent_builder.service import AgentBuilderService
from core.control_api.openapi import document
from core.control_api.service import ControlApiService
from core.deployment_center.api import create as create_deployment, snapshot as deployment_snapshot
from core.deployment_center.service import DeploymentCenter
from core.evidence.service import EvidenceService

from .audit import AuditLogger
from .models import WebConfig


class WebRequestHandler(BaseHTTPRequestHandler):
    server_version = "SI-Agents-Web/1"
    protocol_version = "HTTP/1.1"

    @property
    def web_server(self) -> "WebServer":
        return self.server  # type: ignore[return-value]

    def _request_id(self) -> str:
        value = self.headers.get("X-Request-ID", "").strip()
        return value[:128] if value else f"web-{secrets.token_hex(8)}"

    def _authorized(self) -> bool:
        if self.web_server.config.is_loopback:
            return True
        expected = self.web_server.config.auth_token
        supplied = self.headers.get("Authorization", "")
        if not expected or not supplied.startswith("Bearer "):
            return False
        return secrets.compare_digest(supplied.removeprefix("Bearer ").strip(), expected)

    def _cors_origin(self) -> str | None:
        origin = self.headers.get("Origin")
        if origin and origin in self.web_server.config.cors_origins:
            return origin
        return None

    def _headers(self, *, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def _send(self, status: int, payload: object, *, content_type: str = "application/json; charset=utf-8") -> None:
        if content_type.startswith("application/json"):
            body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        elif isinstance(payload, bytes):
            body = payload
        else:
            body = str(payload).encode("utf-8")
        self.send_response(status)
        self._headers(content_type=content_type, length=len(body))
        self.send_header("X-Request-ID", self._request_id())
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, code: str) -> None:
        self._send(status, {"error": code, "message": "request could not be completed", "request_id": self._request_id()})

    def _audit(self, status: int, metadata: dict[str, object] | None = None) -> None:
        self.web_server.audit.record(request_id=self._request_id(), method=self.command, path=urlparse(self.path).path, status=status, metadata=metadata)

    def _read_json(self) -> dict[str, object]:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ValueError("invalid content type")
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ValueError("missing content length")
        length = int(raw_length)
        if length < 0 or length > 1_048_576:
            raise ValueError("request too large")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise TypeError("JSON object required")
        return payload

    def _api_get(self, path: str) -> object:
        service = self.web_server.service
        routes: dict[str, object] = {
            "/api/v1": service.snapshot().as_dict(), "/api/v1/health": {"status": "ok", "api_version": "v1"},
            "/api/v1/openapi.json": document(), "/api/v1/agents": service.agents(), "/api/v1/teams": service.teams(),
            "/api/v1/workflows": service.workflows(), "/api/v1/organization": service.organization(),
            "/api/v1/skills": service.skills(), "/api/v1/memory": service.memory(),
            "/api/v1/governance": service.governance_state(), "/api/v1/evidence": service.evidence(),
            "/api/v1/evidence/records": self.web_server.evidence.list(),
            "/api/v1/environments": service.environments(), "/api/v1/harnesses": service.harnesses(),
            "/api/v1/deployments": deployment_snapshot(self.web_server.deployment),
            "/api/v1/settings": service.settings(), "/api/v1/visualization": service.visualization(),
            "/api/v1/events": service.events(), "/api/v1/runs": service.runs(),
            "/api/v1/agent-builder": self.web_server.builder.list(),
        }
        if path == "/api/v1/control-center":
            return {"snapshot": service.snapshot().as_dict(), "settings": service.settings(), "environments": service.environments(),
                    "harnesses": service.harnesses(), "deployments": deployment_snapshot(self.web_server.deployment),
                    "evidence": service.evidence(), "visualization": service.visualization(), "agent_builder": self.web_server.builder.list()}
        if path.startswith("/api/v1/evidence/"):
            evidence_id = path.removeprefix("/api/v1/evidence/")
            if evidence_id.endswith("/verify"):
                raise KeyError(path)
            return self.web_server.evidence.get(evidence_id)
        if path.startswith("/api/v1/agent-builder/drafts/"):
            draft_id = path.removeprefix("/api/v1/agent-builder/drafts/")
            if draft_id.endswith("/test"):
                return self.web_server.builder.test(draft_id.removesuffix("/test")).as_dict()
            return self.web_server.builder.get(draft_id)
        if path.startswith("/api/v1/agent-builder/from/"):
            return self.web_server.builder.from_agent(path.removeprefix("/api/v1/agent-builder/from/"))
        if path in routes:
            return routes[path]
        if path.startswith("/api/v1/runs/"):
            suffix = path.removeprefix("/api/v1/runs/")
            if suffix.endswith("/timeline"):
                return self.web_server.evidence.timeline(suffix.removesuffix("/timeline"))
            return service.get_run(suffix)
        raise KeyError(path)

    def do_OPTIONS(self) -> None:
        origin = self.headers.get("Origin")
        if origin and origin not in self.web_server.config.cors_origins:
            self._error(403, "cors_denied")
            self._audit(403)
            return
        self.send_response(204)
        self._headers(content_type="text/plain; charset=utf-8", length=0)
        if origin:
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Request-ID")
            self.send_header("Access-Control-Max-Age", "300")
        self.end_headers()

    def do_GET(self) -> None:
        if not self._authorized():
            self._send(401, {"error": "authentication_required", "message": "request could not be completed", "request_id": self._request_id()})
            self._audit(401)
            return
        path = urlparse(self.path).path.rstrip("/") or "/"
        static = {
            "/": ("index.html", "text/html; charset=utf-8"), "/agent-builder": ("agent-builder.html", "text/html; charset=utf-8"),
            "/deployments": ("deployment.html", "text/html; charset=utf-8"), "/assets/app.js": ("app.js", "text/javascript; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/assets/app.css": ("app.css", "text/css; charset=utf-8"),
            "/app.css": ("app.css", "text/css; charset=utf-8"), "/assets/agent-builder.html": ("agent-builder.html", "text/html; charset=utf-8"),
            "/assets/builder.js": ("builder.js", "text/javascript; charset=utf-8"), "/assets/builder.css": ("builder.css", "text/css; charset=utf-8"),
            "/assets/evidence.html": ("evidence.html", "text/html; charset=utf-8"), "/assets/evidence.js": ("evidence.js", "text/javascript; charset=utf-8"),
            "/assets/evidence.css": ("evidence.css", "text/css; charset=utf-8"), "/assets/deployment.html": ("deployment.html", "text/html; charset=utf-8"),
            "/assets/deployment.js": ("deployment.js", "text/javascript; charset=utf-8"), "/assets/deployment.css": ("deployment.css", "text/css; charset=utf-8"),
        }
        if path in static:
            filename, content_type = static[path]
            body = (Path(__file__).parent / "assets" / filename).read_bytes()
            self._send(200, body, content_type=content_type)
            self._audit(200)
            return
        try:
            payload = self._api_get(path)
        except KeyError:
            self._error(404, "not_found")
            self._audit(404)
            return
        except Exception:
            self._error(500, "internal_error")
            self._audit(500)
            return
        self._send(200, payload)
        self._audit(200)

    def do_POST(self) -> None:
        if not self._authorized():
            self._send(401, {"error": "authentication_required", "message": "request could not be completed", "request_id": self._request_id()})
            self._audit(401)
            return
        path = urlparse(self.path).path.rstrip("/")
        try:
            payload = self._read_json()
            if path == "/api/v1/runs":
                result = self.web_server.service.create_run(payload)
                self._send(202, result)
                self._audit(202, {"mutation": "run_create", "decision": "accepted", "run_id": result.get("id")})
                return
            if path == "/api/v1/evidence":
                result = self.web_server.evidence.record(payload)
                self._send(201, result)
                self._audit(201, {"mutation": "evidence_record", "evidence_id": result.get("id"), "kind": result.get("kind")})
                return
            if path.startswith("/api/v1/evidence/") and path.endswith("/verify"):
                evidence_id = path.removeprefix("/api/v1/evidence/").removesuffix("/verify")
                state = payload.get("verification")
                if not isinstance(state, str):
                    raise ValueError("verification is required")
                result = self.web_server.evidence.verify(evidence_id, state)
                self._send(200, result)
                self._audit(200, {"mutation": "evidence_verify", "evidence_id": evidence_id, "verification": state})
                return
            if path == "/api/v1/deployments":
                result = create_deployment(self.web_server.deployment, payload)
                self._send(201, result)
                self._audit(201, {"mutation": "deployment_plan_create", "plan_id": result.get("id"), "harness_id": result.get("harness_id")})
                return
            if path == "/api/v1/agent-builder/validate":
                result = self.web_server.builder.validate_payload(payload)
                self._send(200, result.as_dict())
                self._audit(200, {"mutation": "agent_builder_validate", "valid": result.valid})
                return
            if path == "/api/v1/agent-builder/drafts":
                result = self.web_server.builder.save(payload)
                self._send(201, result)
                self._audit(201, {"mutation": "agent_builder_save", "draft_id": result.get("id")})
                return
            if path.startswith("/api/v1/agent-builder/drafts/") and path.endswith("/archive"):
                draft_id = path.removeprefix("/api/v1/agent-builder/drafts/").removesuffix("/archive")
                result = self.web_server.builder.archive(draft_id)
                self._send(200, result)
                self._audit(200, {"mutation": "agent_builder_archive", "draft_id": draft_id})
                return
            if path.startswith("/api/v1/agent-builder/drafts/") and path.endswith("/test"):
                draft_id = path.removeprefix("/api/v1/agent-builder/drafts/").removesuffix("/test")
                result = self.web_server.builder.test(draft_id)
                self._send(200, result.as_dict())
                self._audit(200, {"mutation": "agent_builder_test", "draft_id": draft_id, "valid": result.valid})
                return
            self._error(404, "not_found")
            self._audit(404)
            return
        except PermissionError:
            self._error(403, "governance_denied")
            self._audit(403)
        except KeyError:
            self._error(404, "not_found")
            self._audit(404)
        except (TypeError, ValueError, UnicodeDecodeError):
            self._error(400, "invalid_request")
            self._audit(400, {"mutation": "request", "decision": "invalid"})
        except Exception:
            self._error(500, "internal_error")
            self._audit(500, {"mutation": "request", "decision": "error"})

    def log_message(self, format: str, *args: object) -> None:
        return


class WebServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, config: WebConfig, service: ControlApiService, audit: AuditLogger) -> None:
        config.validate()
        super().__init__((config.host, config.port), WebRequestHandler)
        self.config = config
        self.service = service
        self.builder = AgentBuilderService(service.root)
        self.evidence = EvidenceService(str(Path(service.root) / ".si" / "evidence.v1.json"))
        self.deployment = DeploymentCenter(service.root)
        self.audit = audit


def create_server(config: WebConfig, service: ControlApiService) -> WebServer:
    path = config.audit_log or Path.home() / ".local" / "state" / "si-agents" / "web-audit.jsonl"
    return WebServer(config, service, AuditLogger(path))


def serve(config: WebConfig, service: ControlApiService) -> None:
    server = create_server(config, service)
    stopped = Event()

    def stop(_signum: int, _frame: object) -> None:
        stopped.set()

    old_int = signal.signal(signal.SIGINT, stop)
    old_term = signal.signal(signal.SIGTERM, stop)
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
    thread.start()
    try:
        print(f"SI Web listening on http://{config.host}:{server.server_port}")
        while thread.is_alive() and not stopped.wait(0.2):
            pass
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        signal.signal(signal.SIGINT, old_int)
        signal.signal(signal.SIGTERM, old_term)
