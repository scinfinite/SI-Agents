import urllib.error
from unittest.mock import patch

from adapters.opencode import OpenCodeAdapter, OpenCodeConfig
from core.runtime.models import InvocationRequest, InvocationStatus, RuntimeKind


def request(session_id: str | None = None) -> InvocationRequest:
    return InvocationRequest(
        request_id="req-23",
        capability_id="chat",
        input="hello",
        project_id="project",
        session_id=session_id,
        metadata=(("model", "test-model"), ("agent", "developer")),
    )


def test_metadata_and_capabilities_are_declared() -> None:
    adapter = OpenCodeAdapter()
    assert adapter.metadata.harness_id == "opencode"
    assert adapter.metadata.kind is RuntimeKind.AGENT
    assert adapter.capabilities.tool_calls
    assert adapter.capabilities.session_continuity
    assert adapter.capabilities.cancellation
    assert not adapter.capabilities.streaming


def test_config_rejects_invalid_values() -> None:
    try:
        OpenCodeConfig(base_url="")
        raise AssertionError("empty URL must be rejected")
    except ValueError:
        pass


def test_invoke_creates_session_and_maps_message() -> None:
    adapter = OpenCodeAdapter(OpenCodeConfig(base_url="http://example.test"))
    with patch("urllib.request.urlopen") as urlopen:
        response_obj = urlopen.return_value.__enter__.return_value
        response_obj.read.side_effect = [
            b'{"id":"ses_123"}',
            b'{"parts":[{"type":"text","text":"world"}]}',
        ]
        result = adapter.invoke(request())
    assert result.status is InvocationStatus.COMPLETED
    assert result.output == "world"
    assert result.events[0].data == {"session_id": "ses_123"}
    assert urlopen.call_count == 2


def test_invoke_reuses_existing_session() -> None:
    adapter = OpenCodeAdapter(OpenCodeConfig(base_url="http://example.test"))
    with patch("urllib.request.urlopen") as urlopen:
        response_obj = urlopen.return_value.__enter__.return_value
        response_obj.read.return_value = b'{"parts":[{"type":"text","text":"continued"}]}'
        result = adapter.invoke(request("ses_existing"))
    assert result.status is InvocationStatus.COMPLETED
    assert result.output == "continued"
    assert urlopen.call_count == 1


def test_invoke_maps_http_429_to_retryable_failure() -> None:
    adapter = OpenCodeAdapter(OpenCodeConfig(base_url="http://example.test"))
    with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("u", 429, "rate", {}, None)):
        result = adapter.invoke(request("ses_existing"))
    assert result.status is InvocationStatus.FAILED
    assert result.error is not None
    assert result.error.retryable


def test_cancel_uses_session_abort() -> None:
    adapter = OpenCodeAdapter(OpenCodeConfig(base_url="http://example.test"))
    with patch("urllib.request.urlopen") as urlopen:
        response_obj = urlopen.return_value.__enter__.return_value
        response_obj.read.return_value = b"true"
        assert adapter.cancel("ses_existing")
    assert urlopen.call_count == 1
