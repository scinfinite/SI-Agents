"""Phase 48 OmniRoute model/provider adapter."""
from __future__ import annotations

import json
import os
import socket
import threading
import urllib.error
import urllib.parse
import urllib.request
from builtins import RuntimeError as BuiltinRuntimeError
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeCapabilities,
    RuntimeError as SIRuntimeError,
    RuntimeErrorCode,
    RuntimeEvent,
    RuntimeEventType,
    RuntimeKind,
)
from core.runtime.protocol import HarnessAdapter, HarnessMetadata


class OmniRouteTransportError(BuiltinRuntimeError):
    """Internal transport failure; upstream response bodies are never exposed."""

    def __init__(self, status: int | None, kind: str, retry_after: float | None = None) -> None:
        self.status = status
        self.kind = kind
        self.retry_after = retry_after
        super().__init__(kind)


class OmniRouteTransport(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
        token: str | None = None,
    ) -> Any: ...


@dataclass(frozen=True)
class OmniRouteCredentialRef:
    """Reference to a credential; the credential value is never persisted."""

    name: str
    env_var: str = "OMNIROUTE_TOKEN"

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.env_var.strip():
            raise ValueError("credential reference requires name and env_var")

    def resolve(self) -> str | None:
        return os.environ.get(self.env_var)


@dataclass(frozen=True)
class OmniRouteModel:
    model_id: str
    provider_id: str | None = None
    capabilities: frozenset[str] = frozenset()
    context_window: int | None = None
    input_cost: float | None = None
    output_cost: float | None = None
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id is required")
        if self.context_window is not None and self.context_window < 0:
            raise ValueError("context_window must be non-negative")
        if self.input_cost is not None and self.input_cost < 0:
            raise ValueError("input_cost must be non-negative")
        if self.output_cost is not None and self.output_cost < 0:
            raise ValueError("output_cost must be non-negative")


@dataclass(frozen=True)
class OmniRoutePolicy:
    """Selection preferences only; policy never grants authority."""

    required_capabilities: frozenset[str] = frozenset()
    preferred_models: tuple[str, ...] = ()
    fallback_models: tuple[str, ...] = ()
    max_input_cost: float | None = None
    max_output_cost: float | None = None

    def __post_init__(self) -> None:
        if self.max_input_cost is not None and self.max_input_cost < 0:
            raise ValueError("max_input_cost must be non-negative")
        if self.max_output_cost is not None and self.max_output_cost < 0:
            raise ValueError("max_output_cost must be non-negative")


class UrllibOmniRouteTransport:
    """Small OpenAI-compatible HTTP transport with secret-safe errors."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _url(self, path: str, query: Mapping[str, str] | None = None) -> str:
        url = f"{self.base_url}/{path.lstrip('/')}"
        return f"{url}?{urllib.parse.urlencode(query)}" if query else url

    def request(self, method: str, path: str, *, query: Mapping[str, str] | None = None, body: Mapping[str, Any] | None = None, token: str | None = None) -> Any:
        payload = json.dumps(body).encode() if body is not None else None
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(self._url(path, query), data=payload, method=method.upper(), headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                retry_after = response.headers.get("Retry-After")
        except urllib.error.HTTPError as exc:
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            parsed_retry = None
            try:
                parsed_retry = float(retry_after) if retry_after is not None else None
            except (TypeError, ValueError):
                parsed_retry = None
            raise OmniRouteTransportError(exc.code, "http_error", parsed_retry) from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            raise OmniRouteTransportError(None, "transport_error") from exc
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OmniRouteTransportError(None, "invalid_json") from exc


class OmniRouteBridge(HarnessAdapter):
    """Use OmniRoute as SI's downstream model/provider access layer."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:20128",
        *,
        version: str = "unknown",
        transport: OmniRouteTransport | None = None,
        timeout: float = 30.0,
        allow_remote: bool = False,
        credential_ref: OmniRouteCredentialRef | None = None,
    ) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OmniRoute base_url must be an absolute HTTP(S) URL")
        if not allow_remote and not self._is_loopback(parsed.hostname):
            raise ValueError("remote OmniRoute endpoints require allow_remote=True")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.base_url = base_url.rstrip("/")
        self._transport = transport or UrllibOmniRouteTransport(self.base_url, timeout)
        self._metadata = HarnessMetadata("omniroute", RuntimeKind.API, version)
        self._capabilities = RuntimeCapabilities(streaming=True, cancellation=False, tool_calls=False, structured_output=True, session_continuity=False)
        self._credential_ref = credential_ref or OmniRouteCredentialRef("default")
        self._lock = threading.RLock()
        self._catalog: tuple[OmniRouteModel, ...] = ()

    @staticmethod
    def _is_loopback(hostname: str | None) -> bool:
        if not hostname:
            return False
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            return True
        try:
            return hostname == socket.gethostbyname("localhost")
        except OSError:
            return False

    @property
    def metadata(self) -> HarnessMetadata:
        return self._metadata

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return self._capabilities

    @property
    def credential_ref(self) -> OmniRouteCredentialRef:
        return self._credential_ref

    def health(self) -> Mapping[str, Any]:
        result = self._request("GET", "/health")
        if not isinstance(result, Mapping):
            raise OmniRouteTransportError(None, "invalid_health_response")
        return result

    def list_models(self, *, refresh: bool = True) -> tuple[OmniRouteModel, ...]:
        if not refresh:
            with self._lock:
                return self._catalog
        result = self._request("GET", "/v1/models")
        data = result.get("data", []) if isinstance(result, Mapping) else []
        if not isinstance(data, list):
            raise OmniRouteTransportError(None, "invalid_model_catalog")
        models = tuple(self._parse_model(item) for item in data if isinstance(item, Mapping))
        with self._lock:
            self._catalog = models
        return models

    def select_model(self, policy: OmniRoutePolicy, *, models: tuple[OmniRouteModel, ...] | None = None) -> OmniRouteModel:
        catalog = models if models is not None else self.list_models()
        candidates = [m for m in catalog if policy.required_capabilities <= m.capabilities]
        if policy.max_input_cost is not None:
            candidates = [m for m in candidates if m.input_cost is None or m.input_cost <= policy.max_input_cost]
        if policy.max_output_cost is not None:
            candidates = [m for m in candidates if m.output_cost is None or m.output_cost <= policy.max_output_cost]
        by_id = {m.model_id: m for m in candidates}
        for model_id in (*policy.preferred_models, *policy.fallback_models):
            if model_id in by_id:
                return by_id[model_id]
        if candidates:
            return sorted(candidates, key=lambda m: (m.input_cost if m.input_cost is not None else float("inf"), m.model_id))[0]
        raise LookupError("no OmniRoute model satisfies the requested policy")

    def invoke(self, request: InvocationRequest) -> InvocationResponse:
        try:
            policy = self._policy_from_request(request)
            model = self.select_model(policy)
            result = self._request("POST", "/v1/chat/completions", body=self._completion_body(request, model))
            output = self._extract_output(result)
            usage = self._extract_usage(result)
            event = RuntimeEvent(RuntimeEventType.COMPLETED, request.request_id, 0, output)
            return InvocationResponse(request.request_id, InvocationStatus.COMPLETED, output=output, events=(event,), usage=usage)
        except LookupError as exc:
            return InvocationResponse(request.request_id, InvocationStatus.FAILED, error=SIRuntimeError(RuntimeErrorCode.NOT_SUPPORTED, str(exc), retryable=False))
        except OmniRouteTransportError as exc:
            code = RuntimeErrorCode.TIMEOUT if exc.kind == "transport_error" else RuntimeErrorCode.EXECUTION_FAILED
            retryable = exc.status in {408, 409, 425, 429, 500, 502, 503, 504}
            return InvocationResponse(request.request_id, InvocationStatus.FAILED, error=SIRuntimeError(code, "OmniRoute request failed", retryable=retryable))

    def cancel(self, request_id: str) -> bool:
        return False

    def _request(self, method: str, path: str, *, query: Mapping[str, str] | None = None, body: Mapping[str, Any] | None = None) -> Any:
        return self._transport.request(method, path, query=query, body=body, token=self._credential_ref.resolve())

    @staticmethod
    def _parse_model(item: Mapping[str, Any]) -> OmniRouteModel:
        model_id = item.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            raise OmniRouteTransportError(None, "invalid_model_entry")
        raw_caps = item.get("capabilities")
        capabilities = frozenset(str(value) for value in raw_caps if str(value).strip()) if isinstance(raw_caps, list) else frozenset()
        provider_id = item.get("provider") or item.get("provider_id")
        context = item.get("context_window") or item.get("context_length")
        input_cost = item.get("input_cost")
        output_cost = item.get("output_cost")
        return OmniRouteModel(model_id, str(provider_id) if provider_id else None, capabilities, int(context) if isinstance(context, (int, float)) else None, float(input_cost) if isinstance(input_cost, (int, float)) else None, float(output_cost) if isinstance(output_cost, (int, float)) else None)

    @staticmethod
    def _policy_from_request(request: InvocationRequest) -> OmniRoutePolicy:
        metadata = dict(request.metadata)
        required = frozenset(filter(None, metadata.get("required_capabilities", "").split(",")))
        preferred = tuple(filter(None, metadata.get("preferred_models", "").split(",")))
        fallback = tuple(filter(None, metadata.get("fallback_models", "").split(",")))
        return OmniRoutePolicy(required, preferred, fallback)

    @staticmethod
    def _completion_body(request: InvocationRequest, model: OmniRouteModel) -> dict[str, Any]:
        if isinstance(request.input, Mapping) and isinstance(request.input.get("messages"), list):
            messages = request.input["messages"]
        else:
            text = request.input if isinstance(request.input, str) else json.dumps(request.input, ensure_ascii=False, sort_keys=True)
            messages = [{"role": "user", "content": text}]
        body: dict[str, Any] = {"model": model.model_id, "messages": messages, "stream": False}
        metadata = dict(request.metadata)
        for key in ("temperature", "max_tokens", "response_format"):
            if key not in metadata:
                continue
            value: Any = metadata[key]
            if key == "temperature":
                try:
                    value = float(value)
                except ValueError:
                    continue
            elif key == "max_tokens":
                try:
                    value = int(value)
                except ValueError:
                    continue
            body[key] = value
        return body

    @staticmethod
    def _extract_output(result: Any) -> str:
        if not isinstance(result, Mapping):
            return ""
        choices = result.get("choices", [])
        if not isinstance(choices, list) or not choices:
            return ""
        message = choices[0].get("message") if isinstance(choices[0], Mapping) else None
        content = message.get("content") if isinstance(message, Mapping) else None
        return content if isinstance(content, str) else ""

    @staticmethod
    def _extract_usage(result: Any) -> tuple[tuple[str, int], ...]:
        usage = result.get("usage") if isinstance(result, Mapping) else None
        if not isinstance(usage, Mapping):
            return ()
        values = []
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = usage.get(key)
            if isinstance(value, int) and value >= 0:
                values.append((key, value))
        return tuple(values)
