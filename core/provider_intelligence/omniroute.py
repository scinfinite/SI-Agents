"""OmniRoute OpenAI-compatible gateway integration.

SI-Agents treats OmniRoute as the external model-routing authority. This module
owns only the transport boundary, model-catalog normalization, and failure
classification; it does not duplicate provider credentials, fallback policy,
or provider circuit state.
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


class OmniRouteError(RuntimeError):
    """Transport or protocol error returned by an OmniRoute gateway."""

    def __init__(self, message: str, *, status: int | None = None, retryable: bool = False) -> None:
        super().__init__(message)
        self.status = status
        self.retryable = retryable


@dataclass(frozen=True)
class OmniRouteConfig:
    """Connection policy for an OmniRoute deployment.

    Credentials are accepted only in memory or through an environment variable;
    this class never reads or writes a credential file.
    """

    base_url: str = "http://127.0.0.1:20128"
    api_key: str | None = None
    api_key_env: str = "OMNIROUTE_API_KEY"
    timeout_seconds: float = 30.0
    require_https_remote: bool = True

    def __post_init__(self) -> None:
        parsed = urllib.parse.urlparse(self.base_url.rstrip("/"))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must be an absolute http(s) URL")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not self.api_key_env or not self.api_key_env.replace("_", "").isalnum():
            raise ValueError("api_key_env must be a simple environment variable name")
        if self.require_https_remote and parsed.scheme == "http" and not _is_loopback(parsed.hostname):
            raise ValueError("remote OmniRoute URLs must use HTTPS unless explicitly allowed")

    @property
    def root_url(self) -> str:
        return self.base_url.rstrip("/")

    def resolve_api_key(self, environ: Mapping[str, str] | None = None) -> str | None:
        if self.api_key is not None:
            return self.api_key
        return (environ or os.environ).get(self.api_key_env)


def _is_loopback(hostname: str | None) -> bool:
    if not hostname:
        return False
    if hostname in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        return socket.gethostbyname(hostname).startswith("127.")
    except OSError:
        return False


@dataclass(frozen=True)
class OmniRouteModel:
    model_id: str
    owned_by: str | None = None
    created: int | None = None


@dataclass(frozen=True)
class OmniRouteHealth:
    healthy: bool
    model_count: int
    status: int = 200


class OmniRouteClient:
    """Minimal stdlib-only client for OmniRoute's public OpenAI-compatible API."""

    _RETRYABLE_STATUS = frozenset({408, 409, 425, 429})

    def __init__(self, config: OmniRouteConfig | None = None) -> None:
        self.config = config or OmniRouteConfig()

    def _request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        extra_headers: Mapping[str, str] | None = None,
    ) -> tuple[int, Mapping[str, Any], Mapping[str, str]]:
        url = f"{self.config.root_url}/{path.lstrip('/')}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        key = self.config.resolve_api_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        if extra_headers:
            headers.update(extra_headers)
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read()
                decoded = json.loads(raw.decode("utf-8")) if raw else {}
                if not isinstance(decoded, dict):
                    raise OmniRouteError("OmniRoute returned a non-object JSON response")
                return response.status, decoded, dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            detail = raw.decode("utf-8", errors="replace")
            try:
                parsed = json.loads(detail)
                detail = str(parsed.get("error", parsed)) if isinstance(parsed, dict) else detail
            except json.JSONDecodeError:
                pass
            retryable = exc.code in self._RETRYABLE_STATUS or exc.code >= 500
            raise OmniRouteError(
                f"OmniRoute HTTP {exc.code}: {detail[:500]}", status=exc.code, retryable=retryable
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise OmniRouteError(f"OmniRoute unavailable: {exc}", retryable=True) from exc
        except json.JSONDecodeError as exc:
            raise OmniRouteError("OmniRoute returned invalid JSON") from exc

    def list_models(self) -> tuple[OmniRouteModel, ...]:
        _, payload, _ = self._request("GET", "/v1/models")
        data = payload.get("data")
        if not isinstance(data, list):
            raise OmniRouteError("OmniRoute /v1/models response is missing a data list")
        models: list[OmniRouteModel] = []
        for item in data:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            models.append(
                OmniRouteModel(
                    model_id=item["id"],
                    owned_by=item.get("owned_by") if isinstance(item.get("owned_by"), str) else None,
                    created=item.get("created") if isinstance(item.get("created"), int) else None,
                )
            )
        return tuple(sorted(models, key=lambda model: model.model_id))

    def health(self) -> OmniRouteHealth:
        try:
            models = self.list_models()
        except OmniRouteError as exc:
            return OmniRouteHealth(False, 0, exc.status or 0)
        return OmniRouteHealth(True, len(models), 200)

    def chat_completion(
        self,
        model: str,
        messages: list[Mapping[str, Any]],
        *,
        session_id: str | None = None,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> tuple[str, Mapping[str, Any]]:
        if not model.strip():
            raise ValueError("model must not be empty")
        if not messages:
            raise ValueError("messages must not be empty")
        payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
        if extra:
            payload.update(extra)
        headers: dict[str, str] = {}
        if session_id:
            headers["X-Session-Id"] = session_id
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if request_id:
            headers["X-Request-Id"] = request_id
        _, response, _ = self._request("POST", "/v1/chat/completions", payload, extra_headers=headers)
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise OmniRouteError("OmniRoute response is missing choices")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise OmniRouteError("OmniRoute response is missing textual message content")
        return content, response
