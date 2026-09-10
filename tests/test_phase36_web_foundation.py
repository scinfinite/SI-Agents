"""Phase 36 Web Foundation contract and security tests."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from core.control_api.service import ControlApiService
from core.web.audit import AuditLogger, redact
from core.web.models import WebConfig
from core.web.server import create_server

ROOT = Path(__file__).resolve().parents[1]


def _start_server(tmp_path: Path, **config_kwargs):
    config = WebConfig(port=0, audit_log=tmp_path / "audit.jsonl", **config_kwargs)
    server = create_server(config, ControlApiService(ROOT))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _request(server, path: str, *, method="GET", body=None, headers=None):
    request = Request(f"http://127.0.0.1:{server.server_port}{path}", method=method, data=body, headers=headers or {})
    return urlopen(request, timeout=3)


def test_default_configuration_is_loopback_and_safe():
    config = WebConfig()
    config.validate()
    assert config.is_loopback
    assert config.allow_remote is False


def test_remote_binding_requires_explicit_opt_in():
    with pytest.raises(ValueError, match="explicit allow_remote"):
        WebConfig(host="0.0.0.0").validate()


def test_remote_binding_requires_long_token():
    with pytest.raises(ValueError, match="authentication token"):
        WebConfig(host="0.0.0.0", allow_remote=True).validate()
    with pytest.raises(ValueError, match="at least 32"):
        WebConfig(host="0.0.0.0", allow_remote=True, auth_token="short").validate()


def test_wildcard_cors_is_forbidden():
    with pytest.raises(ValueError, match="wildcard CORS"):
        WebConfig(cors_origins=("*",)).validate()


def test_explicit_cors_origin_is_accepted():
    WebConfig(cors_origins=("https://localhost:3000",)).validate()


def test_index_is_served_with_security_headers(tmp_path):
    server, thread = _start_server(tmp_path)
    try:
        response = _request(server, "/")
        assert response.status == 200
        assert "SI-Agents Web" in response.read().decode()
        assert response.headers["Content-Security-Policy"].startswith("default-src 'self'")
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["Cache-Control"] == "no-store"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_health_is_live_control_api_state(tmp_path):
    server, thread = _start_server(tmp_path)
    try:
        payload = json.loads(_request(server, "/api/v1/health").read())
        assert payload == {"api_version": "v1", "status": "ok"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_unknown_route_is_safe_error(tmp_path):
    server, thread = _start_server(tmp_path)
    try:
        with pytest.raises(HTTPError) as exc:
            _request(server, "/missing")
        assert exc.value.code == 404
        payload = json.loads(exc.value.read())
        assert payload["error"] == "not_found"
        assert "Traceback" not in json.dumps(payload)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_json_mutation_requires_content_type(tmp_path):
    server, thread = _start_server(tmp_path)
    try:
        with pytest.raises(HTTPError) as exc:
            _request(server, "/api/v1/runs", method="POST", body=b"{}")
        assert exc.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_json_mutation_rejects_oversized_body(tmp_path):
    server, thread = _start_server(tmp_path)
    try:
        body = b"{" + b"\"action\":\"" + b"x" * 1_048_580 + b"\"}"
        with pytest.raises(HTTPError) as exc:
            _request(server, "/api/v1/runs", method="POST", body=body, headers={"Content-Type": "application/json"})
        assert exc.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_governance_denial_is_not_exposed_as_exception_details(tmp_path):
    server, thread = _start_server(tmp_path)
    try:
        body = json.dumps({"action": "external", "subject": "untrusted", "credential": True}).encode()
        with pytest.raises(HTTPError) as exc:
            _request(server, "/api/v1/runs", method="POST", body=body, headers={"Content-Type": "application/json"})
        assert exc.value.code == 403
        payload = json.loads(exc.value.read())
        assert payload["error"] == "governance_denied"
        assert "reasons" not in payload
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_accepted_mutation_is_a_queued_run(tmp_path):
    server, thread = _start_server(tmp_path)
    try:
        body = json.dumps({"action": "inspect", "subject": "operator"}).encode()
        response = _request(server, "/api/v1/runs", method="POST", body=body, headers={"Content-Type": "application/json"})
        assert response.status == 202
        payload = json.loads(response.read())
        assert payload["status"] == "queued"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_remote_requires_bearer_auth(tmp_path):
    config = WebConfig(host="0.0.0.0", port=0, allow_remote=True, auth_token="t" * 32, audit_log=tmp_path / "audit.jsonl")
    server = create_server(config, ControlApiService(ROOT))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(HTTPError) as exc:
            _request(server, "/api/v1/health")
        assert exc.value.code == 401
        response = _request(server, "/api/v1/health", headers={"Authorization": "Bearer " + "t" * 32})
        assert response.status == 200
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_cors_rejects_unlisted_preflight(tmp_path):
    server, thread = _start_server(tmp_path, cors_origins=("https://allowed.example",))
    try:
        request = Request(f"http://127.0.0.1:{server.server_port}/api/v1/health", method="OPTIONS", headers={"Origin": "https://evil.example"})
        with pytest.raises(HTTPError) as exc:
            urlopen(request, timeout=3)
        assert exc.value.code == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_redaction_removes_secret_like_keys():
    payload = redact({"token": "secret", "nested": {"api_key": "key", "safe": "ok"}})
    assert payload["token"] == "<redacted>"
    assert payload["nested"]["api_key"] == "<redacted>"
    assert payload["nested"]["safe"] == "ok"


def test_audit_logger_creates_private_jsonl(tmp_path):
    path = tmp_path / "audit.jsonl"
    AuditLogger(path).record(request_id="r1", method="POST", path="/api/v1/runs", status=202, metadata={"token": "do-not-log"})
    assert path.stat().st_mode & 0o077 == 0
    record = json.loads(path.read_text())
    assert record["metadata"]["token"] == "<redacted>"
    assert "do-not-log" not in path.read_text()


def test_audit_logger_never_logs_full_mutation_body(tmp_path):
    path = tmp_path / "audit.jsonl"
    AuditLogger(path).record(request_id="r2", method="POST", path="/api/v1/runs", status=400, metadata={"mutation": "run_create"})
    text = path.read_text()
    assert "mutation" in text
    assert "request body" not in text
