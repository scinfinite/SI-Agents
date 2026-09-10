from __future__ import annotations

import json
import urllib.error
import urllib.request

from tools.registry.contracts import ToolResult


class GitHubTool:
    """Read-only GitHub HTTP adapter. Authentication is intentionally injected by the caller."""

    def __init__(self, *, token: str | None = None, user_agent: str = "SI-Agents/0.1") -> None:
        self.token = token
        self.user_agent = user_agent

    def fetch(self, url: str, *, timeout: float = 15.0) -> ToolResult:
        if not url.strip():
            raise ValueError("URL must not be empty")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": self.user_agent}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                if "json" in response.headers.get("Content-Type", ""):
                    try:
                        return ToolResult(True, value=json.dumps(json.loads(body), indent=2))
                    except json.JSONDecodeError:
                        pass
                return ToolResult(True, value=body)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            return ToolResult(False, error=str(exc))
