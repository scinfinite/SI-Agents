"""Configuration for the OpenCode server adapter."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenCodeConfig:
    """OpenCode server configuration; credentials stay outside SI-Agents."""

    base_url: str = "http://127.0.0.1:4096"
    username: str = "opencode"
    password: str | None = None
    timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if not self.base_url.strip():
            raise ValueError("base_url must not be empty")
        if not self.username.strip():
            raise ValueError("username must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
