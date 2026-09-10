from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.discovery.models import DiscoveryFinding


@dataclass(frozen=True)
class Detection:
    category: str
    name: str
    value: str
    confidence: float
    source: str
    verification: tuple[str, ...] = ()

    def finding(self) -> DiscoveryFinding:
        return DiscoveryFinding(
            category=self.category,
            name=self.name,
            value=self.value,
            confidence=self.confidence,
            source=self.source,
            verification=self.verification,
        )


class Detector(Protocol):
    name: str

    def detect(self, root: Path) -> tuple[Detection, ...]: ...


@dataclass(frozen=True)
class RepositoryDetector:
    """Conservative repository detector using manifests and marker files."""

    name: str = "repository"

    def detect(self, root: Path) -> tuple[Detection, ...]:
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Discovery root is not a directory: {root}")
        checks = (
            ("language", "Python", ("pyproject.toml", "requirements.txt", "setup.py", "\.python-version")),
            ("language", "Java", ("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle")),
            ("language", "Rust", ("Cargo.toml",)),
            ("language", "Go", ("go.mod",)),
            ("language", "JavaScript", ("package.json",)),
            ("language", "TypeScript", ("tsconfig.json",)),
            ("language", "C#", ("*.csproj", "*.sln")),
            ("language", "Dart", ("pubspec.yaml",)),
            ("language", "Kotlin", ("build.gradle.kts",)),
            ("language", "Swift", ("Package.swift",)),
            ("build_system", "Maven", ("pom.xml",)),
            ("build_system", "Gradle", ("build.gradle", "build.gradle.kts")),
            ("build_system", "Cargo", ("Cargo.toml",)),
            ("build_system", "Go Modules", ("go.mod",)),
            ("build_system", "npm", ("package.json",)),
            ("build_system", "Flutter/Dart", ("pubspec.yaml",)),
            ("build_system", "Swift Package Manager", ("Package.swift",)),
        )
        findings: list[Detection] = []
        for category, name, markers in checks:
            matches = [marker for marker in markers if self._exists(root, marker)]
            if not matches:
                continue
            confidence = 1.0 if len(matches) > 1 else 0.9
            findings.append(
                Detection(
                    category=category,
                    name=name,
                    value=", ".join(matches),
                    confidence=confidence,
                    source="repository-marker",
                    verification=("marker-exists",),
                )
            )
        return tuple(findings)

    @staticmethod
    def _exists(root: Path, marker: str) -> bool:
        if "*" in marker:
            return any(root.glob(marker))
        return (root / marker).is_file()
