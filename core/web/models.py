"""Local Web Control Center foundation contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


@dataclass(frozen=True, slots=True)
class WebConfig:
    """Validated transport configuration for the local Web surface."""

    host: str = "127.0.0.1"
    port: int = 8788
    allow_remote: bool = False
    auth_token: str | None = None
    audit_log: Path | None = None
    cors_origins: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.host.strip():
            raise ValueError("web host must not be empty")
        if not 0 <= self.port <= 65535:
            raise ValueError("web port must be between 0 and 65535")
        remote = self.host not in LOOPBACK_HOSTS
        if remote and not self.allow_remote:
            raise ValueError("remote Web binding requires explicit allow_remote=True")
        if self.allow_remote and not self.auth_token:
            raise ValueError("remote Web exposure requires an authentication token")
        if self.auth_token is not None and len(self.auth_token) < 32:
            raise ValueError("Web authentication token must contain at least 32 characters")
        if "*" in self.cors_origins:
            raise ValueError("wildcard CORS is forbidden")
        if any(origin != origin.strip() or not origin.startswith(("http://", "https://")) for origin in self.cors_origins):
            raise ValueError("CORS origins must be explicit absolute HTTP(S) origins")

    @property
    def is_loopback(self) -> bool:
        return self.host in LOOPBACK_HOSTS
