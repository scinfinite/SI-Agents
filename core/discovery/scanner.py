from __future__ import annotations

from pathlib import Path

from core.discovery.detectors import Detector
from core.discovery.models import DiscoveryFinding, DiscoveryReport, DiscoveryStatus


class DiscoveryScanner:
    """Runs registered detectors and produces an evidence-oriented report."""

    def __init__(self, detectors: tuple[Detector, ...]) -> None:
        self._detectors = detectors

    def scan(self, root: Path) -> DiscoveryReport:
        findings: list[DiscoveryFinding] = []
        unknowns: list[str] = []
        experiments: list[str] = []
        for detector in self._detectors:
            try:
                detections = detector.detect(root)
            except Exception as exc:
                unknowns.append(f"detector:{detector.name}: {type(exc).__name__}")
                continue
            findings.extend(detection.finding() for detection in detections)
            if not detections:
                unknowns.append(f"detector:{detector.name}: no finding")
        status = DiscoveryStatus.VERIFIED if findings and not unknowns else DiscoveryStatus.DISCOVERED
        return DiscoveryReport(
            root=str(root),
            status=status,
            findings=tuple(findings),
            unknowns=tuple(sorted(set(unknowns))),
            experiments=tuple(experiments),
        )
