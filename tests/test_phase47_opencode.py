from __future__ import annotations

import pytest

from core.runtime.models import InvocationRequest, InvocationStatus, RuntimeEventType
from core.runtime.opencode import OpenCodeBridge, OpenCodeTransportError


class FakeTransport:
    def __init__(self):
        self.calls: list[tuple[str, str, dict | None, dict | None]] = []
        self.responses = {
            ("GET", "/global/health"): {"healthy": True, "version": "1.2.3"},
            ("POST", "/session"): {"id": "ses_test"},
            ("POST", "/session/ses_test/message"): {"info": {"id": "msg_1"}, "parts": [{"type": "text", "text": "hello"}]},
            ("POST", "/session/ses_stream/prompt_async"): None,
            ("POST", "/session/ses_test/abort"): True,
        }
        self.events: list[dict] = []

    def request(self, method, path, *, query=None, body=None):
        self.calls.append((method, path, dict(query) if query else None, dict(body) if body else None))
        return self.responses.get((method, path))

    def stream(self, path, *, query=None):
        yield from self.events


def request(*, streaming=False, session_id=None):
    return InvocationRequest("opencode", "hello", "project", session_id=session_id, request_id="req_1", streaming=streaming)


def test_loopback_default_and_health_and_session_creation():
    transport = FakeTransport()
    bridge = OpenCodeBridge(transport=transport)
    assert bridge.health()["healthy"] is True
    session = bridge.create_session("/workspace/project")
    assert session.session_id == "ses_test"
    assert transport.calls[1][2] == {"directory": "/workspace/project"}


def test_remote_endpoint_requires_explicit_opt_in():
    with pytest.raises(ValueError):
        OpenCodeBridge("https://example.test:4096")
    OpenCodeBridge("https://example.test:4096", allow_remote=True)


def test_sync_invoke_normalizes_response_and_preserves_request_identity():
    transport = FakeTransport()
    bridge = OpenCodeBridge(transport=transport)
    response = bridge.invoke(request())
    assert response.status == InvocationStatus.COMPLETED
    assert response.request_id == "req_1"
    assert response.output == "hello"
    assert response.events[-1].type == RuntimeEventType.COMPLETED
    assert transport.calls[1][1] == "/session/ses_test/message"


def test_existing_session_and_model_metadata_are_forwarded_without_authority_fields():
    transport = FakeTransport()
    bridge = OpenCodeBridge(transport=transport)
    req = InvocationRequest("opencode", "hello", "project", session_id="ses_test", request_id="req_2", metadata=(("provider_id", "p"), ("model_id", "m"), ("authority_scope", "must-not-forward")))
    response = bridge.invoke(req)
    assert response.status == InvocationStatus.COMPLETED
    body = transport.calls[-1][3]
    assert body["model"] == {"providerID": "p", "modelID": "m"}
    assert "authority_scope" not in body


def test_cancel_aborts_a_known_session():
    transport = FakeTransport()
    bridge = OpenCodeBridge(transport=transport)
    assert bridge.cancel("ses_test") is True
    assert transport.calls[-1][1] == "/session/ses_test/abort"


def test_streaming_filters_events_by_session_and_maps_deltas_and_terminal_event():
    transport = FakeTransport()
    transport.responses[("POST", "/session")] = {"id": "ses_stream"}
    transport.events = [
        {"type": "server.connected", "properties": {}},
        {"type": "message.part.updated", "properties": {"part": {"sessionID": "ses_stream", "type": "text", "text": "Hel"}}},
        {"type": "message.part.updated", "properties": {"part": {"sessionID": "ses_other", "type": "text", "text": "ignore"}}},
        {"type": "message.part.delta", "properties": {"sessionID": "ses_stream", "delta": "lo"}},
        {"type": "session.idle", "properties": {"sessionID": "ses_stream"}},
    ]
    bridge = OpenCodeBridge(transport=transport)
    response = bridge.invoke(request(streaming=True))
    assert response.status == InvocationStatus.COMPLETED
    assert response.output == "Hello"
    assert [event.type for event in response.events] == [RuntimeEventType.DELTA, RuntimeEventType.DELTA, RuntimeEventType.COMPLETED]


def test_streaming_session_error_is_terminal_failure():
    transport = FakeTransport()
    transport.responses[("POST", "/session")] = {"id": "ses_stream"}
    transport.events = [{"type": "session.error", "properties": {"sessionID": "ses_stream"}}]
    bridge = OpenCodeBridge(transport=transport)
    response = bridge.invoke(request(streaming=True))
    assert response.status == InvocationStatus.FAILED
    assert response.error is not None
    assert response.events[-1].type == RuntimeEventType.FAILED


def test_transport_errors_are_normalized_without_leaking_body():
    class Failing(FakeTransport):
        def request(self, method, path, *, query=None, body=None):
            raise OpenCodeTransportError(503, "http_error")

    bridge = OpenCodeBridge(transport=Failing())
    response = bridge.invoke(request())
    assert response.status == InvocationStatus.FAILED
    assert response.error is not None
    assert response.error.retryable is True
    assert response.error.message == "OpenCode transport request failed"
