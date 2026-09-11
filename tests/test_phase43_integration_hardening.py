from __future__ import annotations

import json
from pathlib import Path

from core.hardening.integration import IntegrationAuditor
from core.hardening.release import ReleaseGate

ROOT = Path(__file__).resolve().parents[1]


def test_integration_audit_is_ready_on_repository() -> None:
    report = IntegrationAuditor(ROOT).run()
    assert report.ready, report.as_dict()
    assert all(check.passed for check in report.checks)


def test_integration_audit_fails_closed_for_missing_required_surface(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "core").mkdir()
    report = IntegrationAuditor(tmp_path).run()
    assert not report.ready
    assert any(check.name == "required_surfaces" and not check.passed for check in report.checks)


def test_integration_audit_rejects_deployment_apply_authority(tmp_path: Path) -> None:
    for relative in IntegrationAuditor.REQUIRED_FILES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    catalog = {"version": 1, "divisions": [{"agents": [{}]} for _ in range(18)]}
    (tmp_path / "config/agent-catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
    for relative in ("config/governance.v1.json", "config/organization-expansion.v1.json"):
        (tmp_path / relative).write_text('{"version": 1}', encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "\n".join(f"{name} = 'x'" for name in IntegrationAuditor.REQUIRED_SCRIPTS), encoding="utf-8"
    )
    (tmp_path / "docs/architecture").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/architecture/PHASES.md").write_text(
        "42. Harness Deployment Center\n43. Final v3 Integration & Hardening\n", encoding="utf-8"
    )
    (tmp_path / "core/deployment_center/models.py").write_text("APPLIED = 'applied'", encoding="utf-8")
    report = IntegrationAuditor(tmp_path).run()
    assert not report.ready
    assert any(check.name == "deployment_planning_only" and not check.passed for check in report.checks)


def test_schema_versioned_configs_are_accepted(tmp_path: Path) -> None:
    for relative in IntegrationAuditor.REQUIRED_FILES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    catalog = {
        "divisions": [{"id": str(index)} for index in range(18)],
        "agents": [{"id": str(index)} for index in range(279)],
    }
    (tmp_path / "config/agent-catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
    for relative in ("config/governance.v1.json", "config/organization-expansion.v1.json"):
        (tmp_path / relative).write_text('{"schema_version": "v1"}', encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "\n".join(f"{name} = 'x'" for name in IntegrationAuditor.REQUIRED_SCRIPTS), encoding="utf-8"
    )
    (tmp_path / "docs/architecture").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/architecture/PHASES.md").write_text(
        "42. Harness Deployment Center\n43. Final v3 Integration & Hardening\n", encoding="utf-8"
    )
    report = IntegrationAuditor(tmp_path).run()
    assert report.ready, report.as_dict()


def test_release_gate_requires_every_gate() -> None:
    gate = ReleaseGate()
    result = gate.evaluate(
        tests_passed=True,
        lint_passed=True,
        build_passed=True,
        security_reviewed=True,
        migration_reviewed=False,
        rollback_tested=True,
    )
    assert not result.ready
    assert result.reasons == ("migration_review evidence missing",)
