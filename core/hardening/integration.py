"""Deterministic final-integration audit for the SI-Agents v3 surface."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class IntegrationCheck:
    name: str
    passed: bool
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class IntegrationReport:
    ready: bool
    checks: tuple[IntegrationCheck, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "version": "v1",
            "ready": self.ready,
            "checks": [check.as_dict() for check in self.checks],
        }


class IntegrationAuditor:
    """Check cross-cutting v3 invariants without executing downstream work."""

    REQUIRED_FILES = (
        "config/agent-catalog.json",
        "config/team-catalog.json",
        "config/persona-source-index.json",
        "config/rules.v1.json",
        "config/governance.v1.json",
        "config/organization-expansion.v1.json",
        "core/control_api/service.py",
        "core/web/server.py",
        "core/tui/app.py",
        "core/deployment_center/models.py",
        "core/evidence/models.py",
    )
    REQUIRED_SCRIPTS = ("si", "si-api", "si-web", "si-tui", "si-deploy", "si-verify")

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def run(self) -> IntegrationReport:
        groups = (
            self._files(),
            self._catalogs(),
            self._authority_boundaries(),
            self._packaging(),
            self._documentation(),
        )
        checks = tuple(item for group in groups for item in group)
        return IntegrationReport(all(check.passed for check in checks), checks)

    def _files(self) -> tuple[IntegrationCheck, ...]:
        missing = tuple(path for path in self.REQUIRED_FILES if not (self.root / path).is_file())
        return (
            IntegrationCheck(
                "required_surfaces",
                not missing,
                "all required v3 surfaces present" if not missing else "missing: " + ", ".join(missing),
            ),
        )

    def _catalogs(self) -> tuple[IntegrationCheck, ...]:
        checks: list[IntegrationCheck] = []
        catalog_path = self.root / "config/agent-catalog.json"
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            divisions = catalog.get("divisions", [])
            agents = catalog.get("agents", [])
            valid_divisions = all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in divisions)
            valid_agents = all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in agents)
            division_count = len(divisions)
            agent_count = len(agents)
            valid = valid_divisions and valid_agents and division_count == 18 and agent_count == 279
            checks.append(
                IntegrationCheck(
                    "agent_catalog",
                    valid,
                    f"{agent_count} agents across {division_count} divisions",
                )
            )
        except (OSError, TypeError, ValueError) as exc:
            checks.append(IntegrationCheck("agent_catalog", False, f"unreadable: {exc}"))

        for relative in ("config/governance.v1.json", "config/organization-expansion.v1.json"):
            try:
                payload = json.loads((self.root / relative).read_text(encoding="utf-8"))
                valid = isinstance(payload, dict) and isinstance(payload.get("version"), (int, str))
                checks.append(
                    IntegrationCheck(
                        relative,
                        valid,
                        "valid JSON configuration" if valid else "root/version is invalid",
                    )
                )
            except (OSError, TypeError, ValueError) as exc:
                checks.append(IntegrationCheck(relative, False, f"unreadable: {exc}"))
        return tuple(checks)

    def _authority_boundaries(self) -> tuple[IntegrationCheck, ...]:
        deployment = self.root / "core/deployment_center/models.py"
        source = deployment.read_text(encoding="utf-8") if deployment.is_file() else ""
        forbidden = ("APPLIED", "def apply", "def deploy")
        found = tuple(token for token in forbidden if token in source)
        return (
            IntegrationCheck(
                "deployment_planning_only",
                not found,
                "no apply/deploy state or method in deployment planning"
                if not found
                else "forbidden: " + ", ".join(found),
            ),
        )

    def _packaging(self) -> tuple[IntegrationCheck, ...]:
        try:
            text = (self.root / "pyproject.toml").read_text(encoding="utf-8")
        except OSError as exc:
            return (IntegrationCheck("packaging", False, str(exc)),)
        missing = tuple(script for script in self.REQUIRED_SCRIPTS if f"{script} =" not in text)
        return (
            IntegrationCheck(
                "packaging",
                not missing,
                "all operator entry points declared" if not missing else "missing scripts: " + ", ".join(missing),
            ),
        )

    def _documentation(self) -> tuple[IntegrationCheck, ...]:
        phases = self.root / "docs/architecture/PHASES.md"
        try:
            text = phases.read_text(encoding="utf-8")
        except OSError as exc:
            return (IntegrationCheck("documentation", False, str(exc)),)
        expected = ("42. Harness Deployment Center", "43. Final v3 Integration & Hardening")
        missing = tuple(item for item in expected if item not in text)
        return (
            IntegrationCheck(
                "documentation",
                not missing,
                "phase index contains current and final phase" if not missing else "missing: " + ", ".join(missing),
            ),
        )
