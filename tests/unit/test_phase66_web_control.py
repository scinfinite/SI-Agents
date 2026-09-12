from __future__ import annotations

import threading
import urllib.request
from pathlib import Path

from core.control_api.service import ControlApiService
from core.control_api.web import create_web_control_server


def _serve(tmp_path: Path):
    server = create_web_control_server(ControlApiService(Path.cwd()), host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server, path: str):
    return urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}{path}", timeout=3)


def test_web_root_and_assets_are_same_origin(tmp_path: Path):
    server, thread = _serve(tmp_path)
    try:
        root = _get(server, "/web/")
        assert root.status == 200
        assert "SI-Agents Control Plane" in root.read().decode()
        css = _get(server, "/web/control/styles.css")
        assert css.status == 200
        assert "@media" in css.read().decode()
        js = _get(server, "/web/control/app.js")
        assert js.status == 200
        assert "fetch('/api/v1/health')" in js.read().decode() or "api('/api/v1/health')" in js.read().decode()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_web_api_is_reused_without_second_authority(tmp_path: Path):
    server, thread = _serve(tmp_path)
    try:
        response = _get(server, "/api/v1/health")
        assert response.status == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert '"api_version":"v1"' in response.read().decode()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_web_server_rejects_remote_binding():
    service = ControlApiService(Path.cwd())
    try:
        create_web_control_server(service, host="0.0.0.0", port=0)
    except ValueError as exc:
        assert "localhost-only" in str(exc)
    else:
        raise AssertionError("remote binding must be rejected")


def test_web_static_path_traversal_is_not_served(tmp_path: Path):
    server, thread = _serve(tmp_path)
    try:
        try:
            _get(server, "/web/control/../server.py")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        else:
            raise AssertionError("path traversal must not serve a file")
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
