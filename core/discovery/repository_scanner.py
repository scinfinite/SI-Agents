from __future__ import annotations

from pathlib import Path

from core.discovery.detectors import RepositoryDetector
from core.discovery.models import DiscoveryReport
from core.discovery.scanner import DiscoveryScanner


class RepositoryDiscovery:
    """Default Phase 9 repository-discovery entry point."""

    def __init__(self) -> None:
        self._scanner = DiscoveryScanner((RepositoryDetector(),))

    def scan(self, root: Path) -> DiscoveryReport:
        return self._scanner.scan(root)
