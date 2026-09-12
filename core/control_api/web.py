"""Same-origin web control plane layered on the versioned Control API."""
from __future__ import annotations

import os
import subprocess
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .server import ControlApiHandler
from .service import ControlApiService

_WEB_ROOT = Path(__file__).resolve().parents[2] / "web" / "control"
_MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
_TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".yaml", ".yml", ".toml", ".txt", ".css", ".html", ".sh"}
_MAX_SOURCE_BYTES = 512 * 1024
_MAX_SEARCH_FILES = 250

class WebControlHandler(ControlApiHandler):
    """Serve the UI and retain all API routes/authorization from ControlApiHandler."""
    def _send_static(self, relative: str) -> bool:
        safe = Path(relative)
        if safe.is_absolute() or ".." in safe.parts:
            return False
        path = (_WEB_ROOT / safe).resolve()
        try:
            path.relative_to(_WEB_ROOT.resolve())
        except ValueError:
            return False
        if not path.is_file() or path.suffix not in _MIME:
            return False
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", _MIME[path.suffix])
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.send_header("X-Request-ID", self._request_id())
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        return True
    def _repo_path(self, raw: str) -> Path:
        if not raw or len(raw) > 512:
            raise ValueError("path is required and bounded")
        root = Path(self.service.root).resolve()
        candidate = (root / raw).resolve()
        try:
            relative = candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("path escapes repository root") from exc
        if ".git" in relative.parts or candidate.suffix.lower() not in _TEXT_SUFFIXES:
            raise ValueError("file type is not available in the viewer")
        return candidate
    def _source(self, query: dict[str, list[str]]) -> None:
        path = self._repo_path(query.get("path", [""])[0])
        if not path.is_file():
            raise KeyError(str(path))
        if path.stat().st_size > _MAX_SOURCE_BYTES:
            raise ValueError("source file exceeds viewer size limit")
        text = path.read_text(encoding="utf-8")
        self._send(200, {"path": str(path.relative_to(self.service.root)), "content": text, "bytes": len(text.encode("utf-8"))})
    def _diff(self, query: dict[str, list[str]]) -> None:
        relative = query.get("path", [""])[0]
        path = self._repo_path(relative)
        if not path.is_file():
            raise KeyError(relative)
        result = subprocess.run(["git", "show", "--format=", "--patch", "HEAD", "--", relative], cwd=self.service.root, capture_output=True, text=True, timeout=2, check=False)
        if result.returncode != 0:
            raise ValueError("unable to compute repository diff")
        diff = result.stdout
        if len(diff.encode("utf-8")) > _MAX_SOURCE_BYTES:
            raise ValueError("diff exceeds viewer size limit")
        self._send(200, {"path": relative, "diff": diff, "base": "previous commit when available", "head": "HEAD"})
    def _search(self, query: dict[str, list[str]]) -> None:
        needle = query.get("q", [""])[0].strip()
        if not needle or len(needle) > 128:
            raise ValueError("q is required and bounded")
        needle_lower = needle.lower()
        results = []
        scanned = 0
        root = Path(self.service.root)
        for path in sorted(root.rglob("*")):
            if scanned >= _MAX_SEARCH_FILES:
                break
            if not path.is_file() or ".git" in path.relative_to(root).parts or path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            scanned += 1
            try:
                if path.stat().st_size > _MAX_SOURCE_BYTES:
                    continue
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if needle_lower in text.lower():
                results.append({"path": str(path.relative_to(root)), "match_count": text.lower().count(needle_lower)})
                if len(results) >= 100:
                    break
        self._send(200, {"query": needle, "results": results, "scanned_files": scanned, "bounded": True})
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        if path in {"/web", "/web/", "/web/control", "/web/control/", "/"} and self._send_static("index.html"):
            return
        if path.startswith("/web/control/") and self._send_static(path.removeprefix("/web/control/")):
            return
        if path in {"/api/v1/source", "/api/v1/diff", "/api/v1/search"}:
            try:
                self._authorize(path)
                if path.endswith("/source"):
                    self._source(query)
                elif path.endswith("/diff"):
                    self._diff(query)
                else:
                    self._search(query)
            except PermissionError as exc:
                self._send(403, {"error": "forbidden", "message": str(exc), "request_id": self._request_id()})
            except (TypeError, ValueError) as exc:
                self._send(400, {"error": "invalid_request", "message": str(exc), "request_id": self._request_id()})
            except KeyError:
                self._send(404, {"error": "not_found", "message": "source not found", "request_id": self._request_id()})
            return
        return super().do_GET()

def create_web_control_server(service: ControlApiService, host: str = "127.0.0.1", port: int = 8788, *, auth_token: str | None = None) -> ThreadingHTTPServer:
    """Create the localhost-first web control plane on the same API surface."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Web Control Plane is localhost-only; explicit remote exposure is not supported by this transport")
    server = ThreadingHTTPServer((host, port), WebControlHandler)
    server.control_service = service  # type: ignore[attr-defined]
    from core.evidence.service import EvidenceService
    from .subscriptions import SubscriptionRegistry
    server.evidence_service = EvidenceService(str(Path(service.root) / ".si" / "evidence.v1.json"))  # type: ignore[attr-defined]
    server.subscription_registry = SubscriptionRegistry()  # type: ignore[attr-defined]
    server.idempotency_cache = {}  # type: ignore[attr-defined]
    server.api_token = auth_token if auth_token is not None else os.environ.get("SI_API_TOKEN")  # type: ignore[attr-defined]
    return server
