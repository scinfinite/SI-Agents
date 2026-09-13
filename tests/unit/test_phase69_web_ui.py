from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from core.control_api.service import ControlApiService
from core.web.models import WebConfig
from core.web.server import create_server


def test_production_ui_assets_define_approved_design_contract():
    root = Path(__file__).parents[2] / "core" / "web" / "assets"
    index = (root / "index.html").read_text(encoding="utf-8")
    css = (root / "app.css").read_text(encoding="utf-8")
    js = (root / "app.js").read_text(encoding="utf-8")

    assert "SI-Agents — Control Center" in index
    assert 'data-theme="dark"' in index
    assert 'id="theme-toggle"' in index
    assert 'id="global-search"' in index
    assert 'data-theme="light"' in css
    assert "localStorage.setItem(\"si-agents-theme\"" in js
    assert "prefers-color-scheme: light" in js
    assert "matchMedia" in js
    assert "reduced-motion" in css
    assert "/api/v1/visualization" in js
    assert "showNodeDetail" in js
    assert "No matching records." in js


def test_production_ui_javascript_is_syntax_valid_when_node_is_available():
    node = shutil.which("node")
    if node is None:
        return
    path = Path(__file__).parents[2] / "core" / "web" / "assets" / "app.js"
    result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_production_ui_root_and_all_primary_api_views_are_reachable():
    server = create_server(WebConfig(host="127.0.0.1", port=0), ControlApiService(Path.cwd()))
    try:
        import threading
        import urllib.request

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        for path in ("/", "/assets/app.css", "/assets/app.js"):
            response = urllib.request.urlopen(base + path, timeout=3)
            assert response.status == 200
        for path in ("/api/v1", "/api/v1/health", "/api/v1/agents", "/api/v1/teams", "/api/v1/workflows", "/api/v1/visualization", "/api/v1/evidence", "/api/v1/runs", "/api/v1/organization", "/api/v1/governance", "/api/v1/environments", "/api/v1/harnesses", "/api/v1/settings"):
            response = urllib.request.urlopen(base + path, timeout=3)
            assert response.status == 200
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
