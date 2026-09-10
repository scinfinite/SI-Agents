"""Governed model invocation through an OmniRoute gateway."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.provider_intelligence.omniroute import OmniRouteClient, OmniRouteModel


class OmniRoutePolicyError(ValueError):
    """Raised when a caller asks OmniRoute to violate an SI routing constraint."""


@dataclass(frozen=True)
class OmniRouteInvocation:
    messages: tuple[Mapping[str, Any], ...]
    model: str = "auto"
    session_id: str | None = None
    idempotency_key: str | None = None
    request_id: str | None = None
    max_cost: float | None = None
    max_latency_ms: float | None = None
    allowed_models: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.messages:
            raise ValueError("messages must not be empty")
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("max_cost must be non-negative")
        if self.max_latency_ms is not None and self.max_latency_ms < 0:
            raise ValueError("max_latency_ms must be non-negative")


@dataclass(frozen=True)
class OmniRouteResult:
    model: str
    output: str
    raw: Mapping[str, Any]


class OmniRouteGateway:
    """Use OmniRoute as the single external provider/model routing authority."""

    def __init__(self, client: OmniRouteClient) -> None:
        self.client = client

    def catalog(self) -> tuple[OmniRouteModel, ...]:
        return self.client.list_models()

    def invoke(self, request: OmniRouteInvocation) -> OmniRouteResult:
        # OmniRoute owns provider pricing and latency-aware routing. SI-Agents
        # must not pretend to enforce constraints it cannot observe or prove.
        if request.max_cost is not None:
            raise OmniRoutePolicyError("max_cost requires a verified SI-side cost catalog")
        if request.max_latency_ms is not None:
            raise OmniRoutePolicyError("max_latency_ms requires a verified SI-side latency catalog")

        model = request.model
        if request.allowed_models and model not in request.allowed_models and model != "auto":
            raise OmniRoutePolicyError("requested model is outside the allowed model set")
        if model == "auto" and request.allowed_models:
            raise OmniRoutePolicyError("auto routing cannot be constrained to an SI allowlist")

        output, raw = self.client.chat_completion(
            model,
            list(request.messages),
            session_id=request.session_id,
            idempotency_key=request.idempotency_key,
            request_id=request.request_id,
        )
        return OmniRouteResult(model=model, output=output, raw=raw)
