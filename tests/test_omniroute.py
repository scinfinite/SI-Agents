"""Tests for the OmniRoute gateway integration."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar

import pytest

from core.provider_intelligence.omniroute import OmniRouteClient, OmniRouteConfig, OmniRouteError
from core.provider_intelligence.omniroute_router import (
    OmniRouteGateway,
    OmniRouteInvocation,
    OmniRoutePolicyError,
)


class Handler(BaseHTTPRequestHandler):
    models: ClassVar[list[dict[str, str]]] = [
        {"id": "if/kimi-k2-thinking", "owned_by": "if"},
        {"id": "cc/claude-sonnet", "owned_by": "cc"},
    ]
    response: ClassVar[dict[str, object]] = {
        "choices": [{"message": {"role": "assistant", "content": "OK"}}],
        "usage": {"prompt_tokens": 2, "completion_tokens": 1},
    }
    status: ClassVar[int] = 200
    last_request: ClassVar[dict[str, object] | None] = None

    def log_message(self, *_args):
        pass

    def _send(self, body):
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == "/v1/models":
            self._send({"object": "list", "data": self.models})
            return
        self.status = 404
        self._send({"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        Handler.last_request = json.loads(self.rfile.read(length))
        if self.path == "/v1/chat/completions":
            self._send(self.response)
            return
        self.status = 404
        self._send({"error": "not found"})


@pytest.fixture
def server():
    Handler.status = 200
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        thread.join()


def url(server):
    return f"http://127.0.0.1:{server.server_port}"


def test_config_rejects_remote_http():
    with pytest.raises(ValueError, match="HTTPS"):
        OmniRouteConfig("http://example.com")


def test_config_allows_loopback_http():
    assert OmniRouteConfig("http://127.0.0.1:20128").root_url.endswith("20128")


def test_config_resolves_environment_key(monkeypatch):
    monkeypatch.setenv("TEST_OMNI_KEY", "secret")
    config = OmniRouteConfig(api_key_env="TEST_OMNI_KEY")
    assert config.resolve_api_key() == "secret"


def test_models_are_sorted_and_normalized(server):
    client = OmniRouteClient(OmniRouteConfig(url(server)))
    models = client.list_models()
    assert [model.model_id for model in models] == ["cc/claude-sonnet", "if/kimi-k2-thinking"]


def test_chat_completion_sends_openai_shape_and_session_headers(server):
    client = OmniRouteClient(OmniRouteConfig(url(server)))
    text, raw = client.chat_completion(
        "if/kimi-k2-thinking",
        [{"role": "user", "content": "hello"}],
        session_id="s1",
        idempotency_key="idem-1",
        request_id="req-1",
    )
    assert text == "OK"
    assert raw["usage"]["prompt_tokens"] == 2
    assert Handler.last_request["stream"] is False
    assert Handler.last_request["model"] == "if/kimi-k2-thinking"


def test_health_reports_model_count(server):
    health = OmniRouteClient(OmniRouteConfig(url(server))).health()
    assert health.healthy is True
    assert health.model_count == 2


def test_health_fails_closed_for_bad_port():
    health = OmniRouteClient(OmniRouteConfig("http://127.0.0.1:1", timeout_seconds=0.1)).health()
    assert health.healthy is False


def test_http_429_is_retryable(server):
    Handler.status = 429
    try:
        with pytest.raises(OmniRouteError) as exc:
            OmniRouteClient(OmniRouteConfig(url(server))).list_models()
        assert exc.value.retryable is True
        assert exc.value.status == 429
    finally:
        Handler.status = 200


def test_gateway_invokes_auto_route(server):
    gateway = OmniRouteGateway(OmniRouteClient(OmniRouteConfig(url(server))))
    result = gateway.invoke(
        OmniRouteInvocation(messages=({"role": "user", "content": "hello"},))
    )
    assert result.output == "OK"
    assert result.model == "auto"


def test_gateway_rejects_unprovable_cost_constraint(server):
    gateway = OmniRouteGateway(OmniRouteClient(OmniRouteConfig(url(server))))
    with pytest.raises(OmniRoutePolicyError):
        gateway.invoke(
            OmniRouteInvocation(
                messages=({"role": "user", "content": "x"},),
                max_cost=1,
            )
        )


def test_gateway_rejects_auto_with_allowlist(server):
    gateway = OmniRouteGateway(OmniRouteClient(OmniRouteConfig(url(server))))
    with pytest.raises(OmniRoutePolicyError):
        gateway.invoke(
            OmniRouteInvocation(
                messages=({"role": "user", "content": "x"},),
                allowed_models=frozenset({"if/kimi-k2-thinking"}),
            )
        )
