"""Phase 37 Control Center contract, live-read, and browser-surface tests."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from core.control_api.service import ControlApiService
from core.web.models import WebConfig
from core.web.server import create_server

ROOT = Path(__file__).resolve().parents[1]


def _start(tmp_path: Path):
    server = create_server(WebConfig(port=0, audit_log=tmp_path / "audit.jsonl"), ControlApiService(ROOT))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server, path: str):
    request = Request(f"http://127.0.0.1:{server.server_port}{path}", headers={"Accept": "application/json"})
    return urlopen(request, timeout=3)


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_control_center_endpoints_are_live_read_models(tmp_path):
    server, thread = _start(tmp_path)
    try:
        for path in ("/api/v1", "/api/v1/evidence", "/api/v1/environments", "/api/v1/harnesses", "/api/v1/settings"):
            response = _get(server, path)
            assert response.status == 200
            assert response.headers["Cache-Control"] == "no-store"
            assert isinstance(json.loads(response.read()), dict)
    finally:
        _stop(server, thread)


def test_control_center_aggregate_is_non_executing(tmp_path):
    service = ControlApiService(ROOT)
    payload = service.settings()
    assert payload["execution"]["run_creation"] == "governed and queued only"
    assert payload["execution"]["execution"] == "downstream"
    assert service.evidence()["run_count"] == 0


def test_environment_view_is_sanitized(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_TOKEN", "must-not-appear")
    service = ControlApiService(ROOT)
    payload = json.dumps(service.environments())
    assert "SECRET_TOKEN" not in payload
    assert "must-not-appear" not in payload
    assert "current" in service.environments()


def test_harness_view_reports_registered_adapters_only(tmp_path):
    payload = ControlApiService(ROOT).harnesses()
    assert isinstance(payload, list)
    assert all(set(item) == {"id", "path", "state"} for item in payload)
    assert all(item["state"] == "registered" for item in payload)


def test_control_center_html_contains_all_operator_sections(tmp_path):
    server, thread = _start(tmp_path)
    try:
        response = _get(server, "/")
        html = response.read().decode()
        assert "SI-Agents Control Center" in html
        assert "Control Center navigation" in html
        assert "assets/app.js" in html
        assert "assets/app.css" in html
    finally:
        _stop(server, thread)


def test_control_center_javascript_has_expected_navigation(tmp_path):
    server, thread = _start(tmp_path)
    try:
        response = _get(server, "/assets/app.js")
        js = response.read().decode()
        for label in ("Overview", "Agents", "Teams", "Workflows", "Skills", "Memory", "Knowledge", "Evidence", "Runs", "Organization", "Governance", "Environments", "Harnesses", "Settings"):
            assert label in js
        assert "innerHTML" not in js
        assert "credentials: \"same-origin\"" in js
    finally:
        _stop(server, thread)


def test_refresh_invalidates_view_cache(tmp_path):
    server, thread = _start(tmp_path)
    try:
        response = _get(server, "/api/v1/runs")
        assert json.loads(response.read()) == []
        body = json.dumps({"action": "inspect", "subject": "operator"}).encode()
        request = Request(f"http://127.0.0.1:{server.server_port}/api/v1/runs", method="POST", data=body, headers={"Content-Type": "application/json"})
        assert urlopen(request, timeout=3).status == 202
        response = _get(server, "/api/v1/runs")
        assert len(json.loads(response.read())) == 1
    finally:
        _stop(server, thread)
