"""Read-only repository diagnostics used by the ``si audit`` command."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from core.organization.loader import load_catalog
from core.personas.registry import PersonaRegistry
from core.skills.registry import SkillRegistry
from core.skills.validator import validate_skill

TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".yml", ".yaml", ".txt"}
HIDDEN_UNICODE = {"\u200b", "\u200c", "\u200d", "\ufeff", "\u2060", "\u2066", "\u2067", "\u2068", "\u2069", "\u202a", "\u202b", "\u202c", "\u202d", "\u206a", "\u206b", "\u206c", "\u206d", "\u206e", "\u206f"}
FORBIDDEN_BRANDING = ("Agency" + " Agents", "agency" + "-agents", "E" + "CC")
# Explicit architecture/phase research records may name external systems. Executable,
# package, and operational surfaces remain free of external branding.
ALLOWED_REFERENCE_DOCS = frozenset({
    "README.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/SI_AGENTS_V4_PLAN.md",
    "docs/architecture/MODEL_ROUTING.md",
    "docs/architecture/PHASE_44_EXECUTION_RUNTIME_CONTRACTS.md",
    "docs/architecture/PHASE_44_EXECUTION_RUNTIME.md",
    "docs/architecture/PHASE_45_EVENT_BUS_STATE.md",
    "docs/architecture/PHASE_46_PARALLEL_SCHEDULER_EXECUTOR.md",
    "docs/architecture/PHASE_47_OPENCODE_BRIDGE.md",
    "docs/architecture/PHASE_48_OMNIROUTE_INTEGRATION.md",
})
TRANSIENT_NAMES = {"persona_parity_build.py", "phase29_unique_names.py", "phase29_heading_fix.py", "phase29_list_fix.py", "phase29-test-debug.txt"}

@dataclass(frozen=True)
class AuditCheck:
    name: str
    ok: bool
    detail: str
    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".ci-wheel-venv" in path.parts:
            continue
        if path.suffix in TEXT_SUFFIXES:
            yield path


def _tracked_artifacts(root: Path) -> list[str]:
    if not (root / ".git").exists():
        return []
    try:
        result = subprocess.run(("git", "-C", str(root), "ls-files", "--cached", "--", "*.pyc", "*.pyo", "**/__pycache__/**"), check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line for line in result.stdout.splitlines() if line]


def audit_repository(root: str | Path) -> tuple[AuditCheck, ...]:
    root = Path(root).resolve()
    checks: list[AuditCheck] = []
    required = ("README.md", "pyproject.toml", "config/agent-catalog.json", "config/team-catalog.json", "core/personas/registry.py", "core/skills/models.py", "core/skills/parser.py", "docs/architecture/PHASE_29_AGENT_PERSONA.md", "docs/architecture/PHASE_30_PORTABLE_SKILLS.md", "docs/architecture/PHASE_31_RULES_HOOKS_EVENTS.md")
    missing = [item for item in required if not (root / item).is_file()]
    checks.append(AuditCheck("required-files", not missing, "missing: " + ", ".join(missing) if missing else "all present"))
    try:
        catalog = load_catalog(root / "config/agent-catalog.json")
        checks.append(AuditCheck("agent-catalog", True, f"{len(catalog.all())} agents across {len(catalog.all_divisions())} divisions"))
    except (OSError, TypeError, ValueError) as exc:
        catalog = None
        checks.append(AuditCheck("agent-catalog", False, str(exc)))
    try:
        persona_registry = PersonaRegistry()
        personas = persona_registry.load_directory(root / "agents")
        persona_errors = persona_registry.validate_against_catalog(catalog) if catalog is not None else ("catalog unavailable",)
        checks.append(AuditCheck("persona-registry", not persona_errors, f"{len(personas)} personas" + ("; " + "; ".join(persona_errors[:5]) if persona_errors else "")))
        if catalog is not None:
            checks.append(AuditCheck("persona-count", len(personas) == len(catalog.all()), f"personas={len(personas)}, agents={len(catalog.all())}"))
    except (OSError, TypeError, ValueError) as exc:
        checks.append(AuditCheck("persona-registry", False, str(exc)))
    try:
        skill_registry = SkillRegistry()
        skills = skill_registry.load_directory(root / "skills")
        skill_errors = {skill.id: validate_skill(skill) for skill in skills if validate_skill(skill)}
        checks.append(AuditCheck("skill-registry", not skill_errors, f"{len(skills)} Skills" + ("; invalid: " + ", ".join(skill_errors) if skill_errors else "")))
        index_ok = _skill_index_matches(root, skills)
        checks.append(AuditCheck("skill-index", index_ok, "index matches discovered Skills" if index_ok else "index mismatch"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        checks.append(AuditCheck("skill-registry", False, str(exc)))
    hidden: list[str] = []
    branding: list[str] = []
    for path in _text_files(root):
        relative = str(path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(char in text for char in HIDDEN_UNICODE):
            hidden.append(relative)
        if relative not in ALLOWED_REFERENCE_DOCS and any(term in text for term in FORBIDDEN_BRANDING):
            branding.append(relative)
    checks.append(AuditCheck("hidden-unicode", not hidden, "clean" if not hidden else ", ".join(hidden[:10])))
    checks.append(AuditCheck("external-branding", not branding, "clean" if not branding else ", ".join(branding[:10])))
    transient = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file() and path.name in TRANSIENT_NAMES]
    compiled = _tracked_artifacts(root)
    checks.append(AuditCheck("temporary-artifacts", not transient, "clean" if not transient else ", ".join(transient)))
    checks.append(AuditCheck("compiled-artifacts", not compiled, "clean" if not compiled else ", ".join(compiled[:10])))
    try:
        pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
        ok = "**/*.md" in pyproject
        checks.append(AuditCheck("persona-packaging", ok, "agents Markdown package data configured" if ok else "agents Markdown package data missing"))
    except OSError as exc:
        checks.append(AuditCheck("persona-packaging", False, str(exc)))
    return tuple(checks)


def _skill_index_matches(root: Path, skills) -> bool:
    data = json.loads((root / "skills" / "index.json").read_text(encoding="utf-8"))
    expected = {(skill.id, skill.version) for skill in skills}
    actual = {(item["id"], item["version"]) for item in data.get("skills", [])}
    return data.get("schema") == "si-agents.skill-index.v1" and expected == actual


def audit_summary(root: str | Path) -> dict[str, object]:
    checks = audit_repository(root)
    return {"ok": all(check.ok for check in checks), "checks": [check.as_dict() for check in checks]}