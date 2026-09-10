from __future__ import annotations

from core.discovery.detectors import Detector


class DetectorRegistry:
    """Deterministic registry for discovery detectors."""

    def __init__(self) -> None:
        self._detectors: dict[str, Detector] = {}

    def register(self, detector: Detector) -> None:
        if detector.name in self._detectors:
            raise ValueError(f"Detector already registered: {detector.name}")
        self._detectors[detector.name] = detector

    def get(self, name: str) -> Detector:
        try:
            return self._detectors[name]
        except KeyError as exc:
            raise KeyError(f"Unknown detector: {name}") from exc

    def all(self) -> tuple[Detector, ...]:
        return tuple(self._detectors[name] for name in sorted(self._detectors))
