from __future__ import annotations

from pathlib import Path

import pytest

from core.cli.audit import audit_repository
from core.runtime import (
    InvocationRequest,
    InvocationStatus,
    OmniRouteBridge,
    OmniRouteCredentialRef,
    OmniRouteModel,
    OmniRoutePolicy,
    RuntimeErrorCode,
)


class FakeTransport:
    def __init__(self, responses=None, errors=None):
        self.responses = responses or {}
        self.errors = errors or {}
        self.calls = []

    def request(self, method, path, *, query=None, body=None, token=None):
        self.calls.append((method, path, query, body, token))
        error = self.errors.get((method, path))
        if error:
            raise error
        return self.responses.get((method, path))


def request(**metadata):
    return InvocationRequest(
        capability_id="model.infer",
        input="hello",
        project_id="demo",
        metadata=tuple(metadata.items()),
    )


def test_endpoint_is_loopback_by_default():
    with pytest.raises(ValueError):
        OmniRouteBridge("http://example.com:20128", transport=FakeTransport())
    OmniRouteBridge("http://127.0.0.1:20128", transport=FakeTransport())


def test_remote_endpoint_requires_explicit_opt_in():
    bridge = OmniRouteBridge(
        "https://example.com:20128", allow_remote=True, transport=FakeTransport()
    )
    assert bridge.metadata.harness_id == "omniroute"


def test_health_and_catalog_are_discoverable():
    transport = FakeTransport(
        {
            ("GET", "/health"): {"healthy": True, "providers": 2},
            ("GET", "/v1/models"): {
                "data": [
                    {
                        "id": "fast-model",
                        "provider": "p1",
                        "capabilities": ["text", "code"],
                        "input_cost": 0.2,
                    },
                    {
                        "id": "vision-model",
                        "provider": "p2",
                        "capabilities": ["text", "vision"],
                        "input_cost": 0.5,
                    },
                ]
            },
        }
    )
    bridge = OmniRouteBridge(transport=transport)
    assert bridge.health()["healthy"] is True
    models = bridge.list_models()
    assert models[0].provider_id == "p1"
    assert "vision" in models[1].capabilities
    assert bridge.list_models(refresh=False) == models


def test_capability_aware_preferred_and_fallback_selection():
    bridge = OmniRouteBridge(transport=FakeTransport())
    models = (
        OmniRouteModel("cheap", capabilities=frozenset({"text"}), input_cost=0.1),
        OmniRouteModel(
            "code", capabilities=frozenset({"text", "code"}), input_cost=0.3
        ),
        OmniRouteModel(
            "expensive-code",
            capabilities=frozenset({"text", "code"}),
            input_cost=0.8,
        ),
    )
    policy = OmniRoutePolicy(
        required_capabilities=frozenset({"code"}),
        preferred_models=("missing",),
        fallback_models=("code",),
    )
    assert bridge.select_model(policy, models=models).model_id == "code"
    assert bridge.select_model(
        OmniRoutePolicy(required_capabilities=frozenset({"code"})), models=models
    ).model_id == "code"


def test_cost_policy_rejects_models_without_matching_budget():
    bridge = OmniRouteBridge(transport=FakeTransport())
    models = (OmniRouteModel("a", input_cost=1.0), OmniRouteModel("b", input_cost=2.0))
    with pytest.raises(LookupError):
        bridge.select_model(OmniRoutePolicy(max_input_cost=0.5), models=models)


def test_invocation_uses_openai_compatible_contract_and_usage():
    transport = FakeTransport(
        {
            ("GET", "/v1/models"): {
                "data": [{"id": "router/model", "provider": "router", "capabilities": ["text"]}]
            },
            ("POST", "/v1/chat/completions"): {
                "choices": [{"message": {"content": "world"}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            },
        }
    )
    bridge = OmniRouteBridge(transport=transport)
    response = bridge.invoke(request(preferred_models="router/model"))
    assert response.status is InvocationStatus.COMPLETED
    assert response.output == "world"
    assert response.usage == (("prompt_tokens", 3), ("completion_tokens", 2), ("total_tokens", 5))
    call = transport.calls[-1]
    assert call[3]["model"] == "router/model"
    assert call[3]["messages"] == [{"role": "user", "content": "hello"}]
    assert call[3]["stream"] is False


def test_structured_messages_are_forwarded_without_governance_metadata():
    transport = FakeTransport(
        {
            ("GET", "/v1/models"): {"data": [{"id": "m", "capabilities": ["text"]}]},
            ("POST", "/v1/chat/completions"): {
                "choices": [{"message": {"content": "ok"}}]
            },
        }
    )
    bridge = OmniRouteBridge(transport=transport)
    req = InvocationRequest(
        capability_id="model.infer",
        project_id="p",
        input={"messages": [{"role": "user", "content": "x"}]},
        metadata=(("preferred_models", "m"), ("authority_scope", "admin")),
    )
    assert bridge.invoke(req).output == "ok"
    body = transport.calls[-1][3]
    assert "authority_scope" not in body
    assert body["messages"][0]["content"] == "x"


def test_credential_is_resolved_at_request_time_and_not_stored_as_value(monkeypatch):
    monkeypatch.setenv("SI_OMNI_TEST_TOKEN", "secret-token")
    transport = FakeTransport({("GET", "/health"): {"healthy": True}})
    bridge = OmniRouteBridge(
        transport=transport,
        credential_ref=OmniRouteCredentialRef("prod", "SI_OMNI_TEST_TOKEN"),
    )
    bridge.health()
    assert transport.calls[-1][-1] == "secret-token"
    assert "secret-token" not in repr(bridge.credential_ref)


def test_missing_credential_does_not_fail_discovery(monkeypatch):
    monkeypatch.delenv("OMNIROUTE_TOKEN", raising=False)
    transport = FakeTransport({("GET", "/health"): {"healthy": True}})
    assert OmniRouteBridge(transport=transport).health()["healthy"] is True


def test_rate_limit_error_is_retryable_without_body_leakage():
    from core.runtime.omniroute import OmniRouteTransportError

    transport = FakeTransport(
        errors={("GET", "/v1/models"): OmniRouteTransportError(429, "http_error", 7.0)}
    )
    bridge = OmniRouteBridge(transport=transport)
    response = bridge.invoke(request())
    assert response.status is InvocationStatus.FAILED
    assert response.error is not None and response.error.retryable is True
    assert response.error.code is RuntimeErrorCode.EXECUTION_FAILED
    assert "429" not in response.error.message
    assert "secret" not in response.error.message


def test_network_failure_maps_to_retryable_timeout_without_leaking_transport_details():
    from core.runtime.omniroute import OmniRouteTransportError

    transport = FakeTransport(
        errors={("GET", "/v1/models"): OmniRouteTransportError(None, "transport_error")}
    )
    response = OmniRouteBridge(transport=transport).invoke(request())
    assert response.error is not None
    assert response.error.code is RuntimeErrorCode.TIMEOUT
    assert response.error.retryable is True
    assert "transport_error" not in response.error.message


def test_no_matching_model_is_typed_failure():
    transport = FakeTransport(
        {("GET", "/v1/models"): {"data": [{"id": "text", "capabilities": ["text"]}]}}
    )
    response = OmniRouteBridge(transport=transport).invoke(
        request(required_capabilities="vision")
    )
    assert response.status is InvocationStatus.FAILED
    assert response.error is not None
    assert response.error.code is RuntimeErrorCode.NOT_SUPPORTED


def test_cancellation_is_explicitly_unsupported():
    assert OmniRouteBridge(transport=FakeTransport()).cancel("request") is False


def test_audit_allows_only_declared_integration_reference_documents():
    root = Path(__file__).resolve().parents[1]
    checks = {check.name: check for check in audit_repository(root)}
    assert checks["external-branding"].ok is True
