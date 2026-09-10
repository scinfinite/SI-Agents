"""OpenCode HTTP adapter.

The adapter intentionally speaks the OpenAI-compatible chat-completions shape
used by OpenCode-compatible providers. SI-Agents remains independent of the
OpenCode SDK and never owns provider credentials.
"""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from core.runtime.models import (
    InvocationRequest,
    InvocationResponse,
    InvocationStatus,
    RuntimeCapabilities,
    RuntimeError as RuntimeFailure,
    RuntimeErrorCode,
)
from core.runtime.protocol import HarnessKind, HarnessMetadata

from .config import OpenCodeConfig


@dataclass(frozen=True)
class OpenCodeAdapter:
    config: OpenCodeConfig = OpenCodeConfig()

    @property
    def metadata(self) -> HarnessMetadata:
        return HarnessMetadata(harness_id="opencode", kind=HarnessKind.CLI, version="v1")

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            streaming=True,
            cancellation=False,
            tool_calls=True,
            structured_output=True,
            session_continuity=True,
        )

    def invoke(self, request: InvocationRequest) -> InvocationResponse:
        if request.streaming and not self.capabilities.streaming:
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.REJECTED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.CAPABILITY_UNSUPPORTED,
                    message="OpenCode adapter does not support requested streaming",
                    retryable=False,
                ),
            )

        payload = self._payload(request)
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        endpoint = self.config.base_url.rstrip("/") + "/chat/completions"
        http_request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(http_request, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
            return self._response(request.request_id, json.loads(raw))
        except urllib.error.HTTPError as exc:
            retryable = exc.code in {408, 409, 425, 429} or exc.code >= 500
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.FAILED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.UPSTREAM_ERROR,
                    message=f"OpenCode returned HTTP {exc.code}",
                    retryable=retryable,
                ),
            )
        except (urllib.error.URLError, TimeoutError) as exc:
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.FAILED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.UPSTREAM_UNAVAILABLE,
                    message=f"OpenCode endpoint unavailable: {exc}",
                    retryable=True,
                ),
            )
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            return InvocationResponse(
                request_id=request.request_id,
                status=InvocationStatus.FAILED,
                error=RuntimeFailure(
                    code=RuntimeErrorCode.PROTOCOL_ERROR,
                    message=f"Invalid OpenCode response: {exc}",
                    retryable=False,
                ),
            )

    def cancel(self, request_id: str) -> bool:
        del request_id
        return False

    @staticmethod
    def _payload(request: InvocationRequest) -> dict[str, Any]:
        content = request.input if isinstance(request.input, str) else json.dumps(request.input)
        return {
            "model": str(request.metadata.get("model", "default")),
            "messages": [{"role": "user", "content": content}],
            "stream": request.streaming,
        }

    @staticmethod
    def _response(request_id: str, payload: dict[str, Any]) -> InvocationResponse:
        choices = payload.get("choices", [])
        output: Any = None
        if choices and isinstance(choices[0], dict):
            output = choices[0].get("message", {}).get("content")
        return InvocationResponse(
            request_id=request_id,
            status=InvocationStatus.COMPLETED,
            output=output,
            usage=payload.get("usage", {}) if isinstance(payload.get("usage", {}), dict) else {},
        )
