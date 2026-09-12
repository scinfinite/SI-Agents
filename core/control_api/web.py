"""Same-origin web control plane layered on the versioned Control API."""
from __future__ import annotations

from http.server import ThreadingHTTPServer
from pathlib import Path

from .server import ControlApiHandler
from .service import ControlApiService


_WEB_ROOT = Path(__file__).resolve().parents[2] / "web" / "control"
_MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}


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

    def do_GET(self):
        from urllib.parse import urlparse
        path = urlparse(self.path).path
        if path in {"/web", "/web/", "/web/control", "/web/control/", "/"}:
            if self._send_static("index.html"):
                return
        if path.startswith("/web/control/") and self._send_static(path.removeprefix("/web/control/")):
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
    server.api_token = auth_token if auth_token is not None else __import__("os").environ.get("SI_API_TOKEN")  # type: ignore[attr-defined]
    return server
