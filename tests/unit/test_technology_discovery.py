from pathlib import Path

import pytest

from core.discovery.compatibility import check_declared_toolchain
from core.discovery.detectors import RepositoryDetector
from core.discovery.experimentation import ExperimentRunner
from core.discovery.knowledge_generation import propose_from_findings
from core.discovery.models import DiscoveryFinding, DiscoveryReport, DiscoveryStatus
from core.discovery.registry import DetectorRegistry
from core.discovery.repository_scanner import RepositoryDiscovery
from core.discovery.scanner import DiscoveryScanner


def test_repository_detector_discovers_java_maven_and_typescript(tmp_path: Path) -> None:
    for name in ("pom.xml", "package.json", "tsconfig.json"):
        (tmp_path / name).write_text("{}", encoding="utf-8")
    findings = RepositoryDetector().detect(tmp_path)
    pairs = {(item.category, item.name) for item in findings}
    assert ("language", "Java") in pairs
    assert ("build_system", "Maven") in pairs
    assert ("language", "TypeScript") in pairs


def test_detector_registry_is_deterministic_and_rejects_duplicates() -> None:
    registry = DetectorRegistry()
    detector = RepositoryDetector()
    registry.register(detector)
    assert registry.all() == (detector,)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(detector)


def test_discovery_report_rejects_empty_verified_report() -> None:
    with pytest.raises(ValueError, match="Verified discovery requires findings"):
        DiscoveryReport(".", DiscoveryStatus.VERIFIED)


def test_scanner_keeps_unknowns_when_detector_fails(tmp_path: Path) -> None:
    class Broken:
        name = "broken"

        def detect(self, root: Path):
            raise RuntimeError("boom")

    report = DiscoveryScanner((Broken(),)).scan(tmp_path)
    assert report.status is DiscoveryStatus.DISCOVERED
    assert report.unknowns == ("detector:broken: RuntimeError",)


def test_repository_discovery_requires_real_directory(tmp_path: Path) -> None:
    report = RepositoryDiscovery().scan(tmp_path)
    assert report.root == str(tmp_path)
    assert report.status is DiscoveryStatus.DISCOVERED
    assert report.unknowns


def test_compatibility_uses_declarations_without_execution(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text("<project/>", encoding="utf-8")
    result = check_declared_toolchain(tmp_path, "Java", ("pom.xml",))
    assert result.compatible is True
    assert result.evidence == ("pom.xml",)


def test_compatibility_reports_missing_declaration(tmp_path: Path) -> None:
    result = check_declared_toolchain(tmp_path, "Rust", ("Cargo.toml",))
    assert result.compatible is False


def test_experiment_runner_is_explicit_and_fail_closed(tmp_path: Path) -> None:
    runner = ExperimentRunner()
    passed = runner.run("read", tmp_path, lambda root: "observed")
    assert passed.passed is True
    failed = runner.run("broken", tmp_path, lambda root: 1)  # type: ignore[return-value]
    assert failed.passed is False
    assert "empty experiment observation" in failed.observation


def test_experiment_runner_captures_exceptions(tmp_path: Path) -> None:
    result = ExperimentRunner().run("boom", tmp_path, lambda root: 1 / 0)
    assert result.passed is False
    assert result.observation.startswith("ZeroDivisionError")


def test_knowledge_generation_creates_proposals_not_promotions() -> None:
    finding = DiscoveryFinding(
        category="language",
        name="Java",
        value="pom.xml",
        confidence=0.9,
        source="repository-marker",
        verification=("marker-exists",),
    )
    proposals = propose_from_findings((finding,))
    assert proposals[0].name == "Java"
    assert proposals[0].confidence == 0.9


def test_discovery_finding_validates_confidence() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        DiscoveryFinding("language", "Java", "pom.xml", 1.1, "marker")
