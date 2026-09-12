"""Phase 66 advanced control-plane extension for the existing SI Web server."""
from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .audit import AuditLogger
from .models import WebConfig
from .server import WebRequestHandler, WebServer
from core.control_api.service import ControlApiService


_ROOT = Path(__file__).resolve().parents[2]
_UI = _ROOT / "web" / "control"
_TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".yaml", ".yml", ".toml", ".txt", ".css", ".html", ".sh"}
_MAX_SOURCE = 512 * 1024
_MAX_SEARCH_FILES = 250


class AdvancedWebRequestHandler(WebRequestHandler):
    """Add the Phase 66 UI and bounded repository inspection to the existing server."""

    def _static_control(self, relative: str) -> bool:
        safe = Path(relative)
        if safe.is_absolute() or ".." in safe.parts:
            return False
        path = (_UI / safe).resolve()
        try:
            path.relative_to(_UI.resolve())
        except ValueError:
            return False
        mime = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
        if not path.is_file() or path.suffix not in mime:
            return False
        self._send(200, path.read_bytes(), content_type=mime[path.suffix])
        self._audit(200, {"surface": "phase66_static"})
        return True

    def _repo_path(self, raw: str) -> Path:
        if not raw or len(raw) > 512:
            raise ValueError("path is required and bounded")
        root = Path(self.web_server.service.root).resolve()
        path = (root / raw).resolve()
        relative = path.relative_to(root)
        if ".git" in relative.parts or path.suffix.lower() not in _TEXT_SUFFIXES:
            raise ValueError("path is not available in the repository viewer")
        return path

    def _inspection(self, path: str, query: dict[str, list[str]]) -> None:
        root = Path(self.web_server.service.root).resolve()
        if path == "/api/v1/source":
            target = self._repo_path(query.get("path", [""])[0])
            if not target.is_file():
                raise KeyError(query.get("path", [""])[0])
            if target.stat().st_size > _MAX_SOURCE:
                raise ValueError("source file exceeds viewer size limit")
            self._send(200, {"path": str(target.relative_to(root)), "content": target.read_text(encoding="utf-8")})
            return
        if path == "/api/v1/diff":
            relative = query.get("path", [""])[0]
            target = self._repo_path(relative)
            if not target.is_file():
                raise KeyError(relative)
            result = subprocess.run(["git", "diff", "HEAD~1", "HEAD", "--", relative], cwd=root, capture_output=True, text=True, timeout=2, check=False)
            if result.returncode not in (0, 1):
                raise ValueError("unable to compute repository diff")
            if len(result.stdout.encode("utf-8")) > _MAX_SOURCE:
                raise ValueError("diff exceeds viewer size limit")
            self._send(200, {"path": relative, "base": "HEAD~1", "head": "HEAD", "diff": result.stdout})
            return
        needle = query.get("q", [""])[0].strip()
        if not needle or len(needle) > 128:
            raise ValueError("q is required and bounded")
        results = []
        scanned = 0
        for target in sorted(root.rglob("*")):
            if scanned >= _MAX_SEARCH_FILES:
                break
            if not target.is_file() or ".git" in target.relative_to(root).parts or target.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            scanned += 1
            try:
                if target.stat().st_size > _MAX_SOURCE:
                    continue
                text = target.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            count = text.lower().count(needle.lower())
            if count:
                results.append({"path": str(target.relative_to(root)), "match_count": count})
                if len(results) >= 100:
                    break
        self._send(200, {"query": needle, "results": results, "scanned_files": scanned, "bounded": True})

    def do_GET(self) -> None:
        if not self._authorized():
            return super().do_GET()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        if path in {"/control", "/control/"}:
            self._static_control("index.html")
            return
        if path.startswith("/control/") and self._static_control(path.removeprefix("/control/")):
            return
        if path in {"/api/v1/source", "/api/v1/diff", "/api/v1/search"}:
            try:
                self._inspection(path, query)
                self._audit(200, {"surface": "phase66_inspection"})
            except PermissionError:
                self._error(403, "governance_denied"); self._audit(403)
            except (TypeError, ValueError):
                self._error(400, "invalid_request"); self._audit(400)
            except (KeyError, IndexError):
                self._error(404, "not_found"); self._audit(404)
            except Exception:
                self._error(500, "internal_error"); self._audit(500)
            return
        super().do_GET()


class AdvancedWebServer(WebServer):
    """Existing WebServer configuration with the Phase 66 handler installed."""

    def __init__(self, config: WebConfig, service: ControlApiService, audit: AuditLogger) -> None:
        super().__init__(config, service, audit)
        self.RequestHandlerClass = AdvancedWebRequestHandler


def create_advanced_server(config: WebConfig, service: ControlApiService) -> AdvancedWebServer:
    """Create the existing SI Web server with the Phase 66 control surface."""
    path = config.audit_log or Path.home() / ".local" / "state" / "si-agents" / "web-audit.jsonl"
    return AdvancedWebServer(config, service, AuditLogger(path))
