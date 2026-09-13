import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from adapters.opencode import OpenCodeAdapter, OpenCodeConfig
from core.governance.models import DataClass, GovernanceRequest, RiskLevel
from core.runtime import (
    HarnessRegistry,
    InvocationRequest,
    InvocationStatus,
    RuntimeEngine,
    RuntimeEventType,
    RuntimeSession,
    SessionRegistry,
)
from core.runtime.models import RuntimeErrorCode
from core.runtime.omniroute import OmniRouteBridge, OmniRouteModel


class _FakeOmniTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict | None]] = []

    def request(self, method: str, path: str, *, query=None, body=None, token=None):
        self.calls.append((method, path, body))
        if path == "/health":
            return {"status": "ok"}
        if path == "/v1/models":
            return {
                "data": [
                    {
                        "id": "acceptance-model",
                        "provider": "acceptance-provider",
                        "capabilities": ["chat"],
                        "context_window": 8192,
                        "input_cost": 0,
                        "output_cost": 0,
                    }
                ]
            }
        if path == "/v1/chat/completions":
            return {
                "choices": [{"message": {"content": "production-path-ok"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4},
            }
        raise AssertionError(f"unexpected OmniRoute call: {method} {path}")


class _OpenCodeHandler(BaseHTTPRequestHandler):
    runtime: RuntimeEngine
    calls: list[tuple[str, dict]]

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _json(self, payload: object) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        self.calls.append((self.path, payload))
        if self.path == "/session":
            self._json({"id": "ses_phase70"})
            return
        if self.path == "/session/ses_phase70/message":
            request = InvocationRequest(
                request_id="phase70-runtime",
                capability_id="chat",
                input=payload["parts"][0]["text"],
                project_id="phase70-project",
                metadata=(("preferred_models", "acceptance-model"),),
                governance=GovernanceRequest(
                    "phase70.e2e",
                    RiskLevel.LOW,
                    DataClass.PUBLIC,
                ),
            )
            result = self.runtime.invoke("omniroute", request)
            assert result.status is InvocationStatus.COMPLETED
            self._json({"parts": [{"type": "text", "text": result.output}]})
            return
        if self.path == "/session/ses_phase70/abort":
            self._json(True)
            return
        self.send_error(404)


def _start_server(runtime: RuntimeEngine):
    handler = type("Phase70Handler", (_OpenCodeHandler,), {})
    handler.runtime = runtime
    handler.calls = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, handler


def _runtime() -> tuple[RuntimeEngine, _FakeOmniTransport]:
    transport = _FakeOmniTransport()
    omni = OmniRouteBridge(transport=transport)
    registry = HarnessRegistry()
    registry.register(omni, enabled=True)
    sessions = SessionRegistry()
    sessions.create(RuntimeSession("phase70-session", "phase70-project", "omniroute"))
    return RuntimeEngine(registry=registry, sessions=sessions), transport


def test_phase70_opencode_si_omniroute_path() -> None:
    runtime, transport = _runtime()
    server, handler = _start_server(runtime)
    try:
        adapter = OpenCodeAdapter(
            OpenCodeConfig(base_url=f"http://127.0.0.1:{server.server_port}")
        )
        request = InvocationRequest(
            request_id="phase70-opencode",
            capability_id="chat",
            input="hello production",
            project_id="phase70-project",
            metadata=(("model", "acceptance-model"), ("agent", "developer")),
        )
        with patch.object(OpenCodeAdapter, "_create_session", wraps=adapter._create_session):
            result = adapter.invoke(request)
        assert result.status is InvocationStatus.COMPLETED
        assert result.output == "production-path-ok"
        assert result.events[0].type is RuntimeEventType.COMPLETED
        assert [path for _, path, _ in transport.calls] == [
            "/v1/models",
            "/v1/chat/completions",
        ]
        assert [path for path, _ in handler.calls] == [
            "/session/ses_phase70/message",
        ] or [path for path, _ in handler.calls] == [
            "/session",
            "/session/ses_phase70/message",
        ]
    finally:
        server.shutdown()
        server.server_close()


def test_phase70_governance_denial_stops_downstream_execution() -> None:
    runtime, transport = _runtime()
    request = InvocationRequest(
        request_id="phase70-denied",
        capability_id="chat",
        input="blocked",
        project_id="phase70-project",
        session_id="phase70-session",
        governance=GovernanceRequest(
            "phase70.denied",
            RiskLevel.CRITICAL,
            DataClass.SECRET,
        ),
    )
    result = runtime.invoke("omniroute", request)
    assert result.status is InvocationStatus.FAILED
    assert result.error is not None
    assert result.error.code is RuntimeErrorCode.GOVERNANCE_DENIED
    assert transport.calls == []


def test_phase70_session_isolation_stops_cross_project_execution() -> None:
    runtime, transport = _runtime()
    request = InvocationRequest(
        request_id="phase70-isolation",
        capability_id="chat",
        input="blocked",
        project_id="other-project",
        session_id="phase70-session",
        governance=GovernanceRequest("phase70.isolation", RiskLevel.LOW, DataClass.PUBLIC),
    )
    result = runtime.invoke("omniroute", request)
    assert result.status is InvocationStatus.FAILED
    assert result.error is not None
    assert result.error.code is RuntimeErrorCode.INVALID_REQUEST
    assert transport.calls == []


def test_phase70_cancel_path_remains_harness_scoped() -> None:
    runtime, _transport = _runtime()
    assert runtime.cancel("omniroute", "phase70-request") is False


def test_phase70_model_selection_preserves_fallback_policy() -> None:
    transport = _FakeOmniTransport()
    bridge = OmniRouteBridge(transport=transport)
    models = (
        OmniRouteModel("preferred", capabilities=frozenset({"chat"}), input_cost=1),
        OmniRouteModel("fallback", capabilities=frozenset({"chat"}), input_cost=0),
    )
    selected = bridge.select_model(
        __import__("core.runtime.omniroute", fromlist=["OmniRoutePolicy"]).OmniRoutePolicy(
            required_capabilities=frozenset({"chat"}),
            preferred_models=("missing",),
            fallback_models=("fallback",),
        ),
        models=models,
    )
    assert selected.model_id == "fallback"
