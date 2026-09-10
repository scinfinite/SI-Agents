from unittest.mock import patch

from adapters.opencode import OpenCodeAdapter, OpenCodeConfig
from core.runtime.models import InvocationRequest, InvocationStatus
from core.runtime.protocol import HarnessKind


def request() -> InvocationRequest:
    return InvocationRequest(
        request_id="req-23",
        capability_id="chat",
        input="hello",
        project_id="project",
        metadata={"model": "test-model"},
    )


def test_metadata_and_capabilities_are_declared() -> None:
    adapter = OpenCodeAdapter()
    assert adapter.metadata.harness_id == "opencode"
    assert adapter.metadata.kind is HarnessKind.CLI
    assert adapter.capabilities.streaming
    assert adapter.capabilities.tool_calls
    assert adapter.capabilities.session_continuity
    assert not adapter.capabilities.cancellation


def test_config_rejects_invalid_values() -> None:
    try:
        OpenCodeConfig(base_url="")
        raise AssertionError("empty URL must be rejected")
    except ValueError:
        pass


def test_invoke_maps_openai_compatible_response() -> None:
    adapter = OpenCodeAdapter(OpenCodeConfig(base_url="http://example.test/v1"))
    response_payload = b'{"choices":[{"message":{"content":"world"}}],"usage":{"total_tokens":3}}'
    with patch("urllib.request.urlopen") as urlopen:
        response = urlopen.return_value.__enter__.return_value
        response.read.return_value = response_payload
        result = adapter.invoke(request())
    assert result.status is InvocationStatus.COMPLETED
    assert result.output == "world"
    assert result.usage["total_tokens"] == 3


def test_invoke_maps_http_429_to_retryable_failure() -> None:
    import urllib.error

    adapter = OpenCodeAdapter(OpenCodeConfig(base_url="http://example.test/v1"))
    with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("u", 429, "rate", {}, None)):
        result = adapter.invoke(request())
    assert result.status is InvocationStatus.FAILED
    assert result.error is not None
    assert result.error.retryable


def test_cancel_is_explicitly_unsupported() -> None:
    assert not OpenCodeAdapter().cancel("req-23")
