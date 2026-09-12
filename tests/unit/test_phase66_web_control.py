from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

from core.control_api.service import ControlApiService
from core.control_api.web import create_web_control_server


def _serve(tmp_path: Path, *, token: str | None = None):
    server = create_web_control_server(ControlApiService(Path.cwd()), host="127.0.0.1", port=0, auth_token=token)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server, path: str, *, headers: dict[str, str] | None = None):
    request = urllib.request.Request(f"http://127.0.0.1:{server.server_port}{path}", headers=headers or {})
    return urllib.request.urlopen(request, timeout=3)


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
        assert "api('/api/v1/health')" in js.read().decode()
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


def test_source_search_and_diff_viewers_are_bounded(tmp_path: Path):
    server, thread = _serve(tmp_path)
    try:
        source = json.loads(_get(server, "/api/v1/source?path=README.md").read())
        assert source["path"] == "README.md"
        assert "SI-Agents" in source["content"]
        search = json.loads(_get(server, "/api/v1/search?q=SI-Agents").read())
        assert search["bounded"] is True
        assert isinstance(search["results"], list)
        diff = json.loads(_get(server, "/api/v1/diff?path=README.md").read())
        assert diff["path"] == "README.md"
        assert diff["base"] == "HEAD~1"
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_web_api_authentication_is_inherited(tmp_path: Path):
    server, thread = _serve(tmp_path, token="secret")
    try:
        with __import__("pytest").raises(urllib.error.HTTPError) as exc:
            _get(server, "/api/v1/source?path=README.md")
        assert exc.value.code == 403
        response = _get(server, "/api/v1/source?path=README.md", headers={"Authorization": "Bearer secret"})
        assert response.status == 200
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
        with __import__("pytest").raises(urllib.error.HTTPError) as exc:
            _get(server, "/web/control/../server.py")
        assert exc.value.code == 404
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
