"""Configuration for the OpenCode SI adapter."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenCodeConfig:
    """Transport-neutral OpenCode endpoint configuration.

    SI-Agents never stores OpenCode credentials. Authentication is delegated to
    the OpenCode/OmniRoute deployment environment.
    """

    base_url: str = "http://localhost:20128/v1"
    api_key: str | None = None
    timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if not self.base_url.strip():
            raise ValueError("base_url must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
