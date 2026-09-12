from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from core.control_api.service import ControlApiService
from core.web.advanced import create_advanced_server
from core.web.models import WebConfig


def _server():
    config = WebConfig(host="127.0.0.1", port=0)
    server = create_advanced_server(config, ControlApiService(Path.cwd()))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server, path: str, headers: dict[str, str] | None = None):
    request = urllib.request.Request(f"http://127.0.0.1:{server.server_port}{path}", headers=headers or {})
    return urllib.request.urlopen(request, timeout=3)


def _close(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_existing_web_server_exposes_phase66_control_surface():
    server, thread = _server()
    try:
        page = _get(server, "/control/")
        assert page.status == 200
        assert "Advanced Web Control Plane" in page.read().decode()
        health = json.loads(_get(server, "/api/v1/health").read())
        assert health["api_version"] == "v1"
        source = json.loads(_get(server, "/api/v1/source?path=README.md").read())
        assert source["path"] == "README.md"
    finally:
        _close(server, thread)


def test_inspection_never_exposes_git_paths():
    server, thread = _server()
    try:
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get(server, "/api/v1/source?path=.git/config")
        assert exc.value.code == 400
    finally:
        _close(server, thread)


def test_remote_server_keeps_existing_auth_boundary():
    token = "s" * 32
    config = WebConfig(host="0.0.0.0", port=0, allow_remote=True, auth_token=token)
    server = create_advanced_server(config, ControlApiService(Path.cwd()))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get(server, "/control/")
        assert exc.value.code == 401
        page = _get(server, "/control/", {"Authorization": f"Bearer {token}"})
        assert page.status == 200
    finally:
        _close(server, thread)
