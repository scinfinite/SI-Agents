"""Read-only repository diagnostics used by the ``si audit`` command."""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from core.organization.loader import load_catalog
from core.personas.registry import PersonaRegistry


TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".yml", ".yaml", ".txt"}
HIDDEN_UNICODE = {
    "\u200b", "\u200c", "\u200d", "\ufeff", "\u2060", "\u2066", "\u2067", "\u2068", "\u2069",
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e", "\u206a", "\u206b", "\u206c", "\u206d", "\u206e", "\u206f",
}
FORBIDDEN_BRANDING = ("Agency" + " Agents", "agency" + "-agents", "E" + "CC")
TRANSIENT_NAMES = {
    "persona_parity_build.py",
    "phase29_unique_names.py",
    "phase29_heading_fix.py",
    "phase29_list_fix.py",
    "phase29-test-debug.txt",
}


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
    git_dir = root / ".git"
    if not git_dir.exists():
        return []
    try:
        result = subprocess.run(
            (
                "git", "-C", str(root), "ls-files", "--cached", "--",
                "*.pyc", "*.pyo", "**/__pycache__/**",
            ),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line for line in result.stdout.splitlines() if line]


def audit_repository(root: str | Path) -> tuple[AuditCheck, ...]:
    """Run deterministic, read-only checks over the shipped repository."""
    root = Path(root).resolve()
    checks: list[AuditCheck] = []

    required = (
        "README.md",
        "pyproject.toml",
        "config/agent-catalog.json",
        "config/team-catalog.json",
        "core/personas/registry.py",
        "docs/architecture/PHASE_29.md",
    )
    missing = [item for item in required if not (root / item).is_file()]
    checks.append(
        AuditCheck(
            "required-files",
            not missing,
            "missing: " + ", ".join(missing) if missing else "all present",
        )
    )

    try:
        catalog = load_catalog(root / "config/agent-catalog.json")
        checks.append(
            AuditCheck(
                "agent-catalog",
                True,
                f"{len(catalog.all())} agents across {len(catalog.all_divisions())} divisions",
            )
        )
    except (OSError, TypeError, ValueError) as exc:
        catalog = None
        checks.append(AuditCheck("agent-catalog", False, str(exc)))

    registry = PersonaRegistry()
    try:
        personas = registry.load_directory(root / "agents")
        persona_errors = (
            registry.validate_against_catalog(catalog)
            if catalog is not None
            else ("catalog unavailable",)
        )
        detail = f"{len(personas)} personas"
        if persona_errors:
            detail += "; " + "; ".join(persona_errors[:5])
        checks.append(AuditCheck("persona-registry", not persona_errors, detail))
        if catalog is not None:
            checks.append(
                AuditCheck(
                    "persona-count",
                    len(personas) == len(catalog.all()),
                    f"personas={len(personas)}, agents={len(catalog.all())}",
                )
            )
    except (OSError, TypeError, ValueError) as exc:
        checks.append(AuditCheck("persona-registry", False, str(exc)))

    hidden: list[str] = []
    branding: list[str] = []
    for path in _text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(char in text for char in HIDDEN_UNICODE):
            hidden.append(str(path.relative_to(root)))
        if any(term in text for term in FORBIDDEN_BRANDING):
            branding.append(str(path.relative_to(root)))
    checks.append(AuditCheck("hidden-unicode", not hidden, "clean" if not hidden else ", ".join(hidden[:10])))
    checks.append(AuditCheck("external-branding", not branding, "clean" if not branding else ", ".join(branding[:10])))

    transient = [
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and path.name in TRANSIENT_NAMES
    ]
    compiled = _tracked_artifacts(root)
    checks.append(AuditCheck("temporary-artifacts", not transient, "clean" if not transient else ", ".join(transient)))
    checks.append(AuditCheck("compiled-artifacts", not compiled, "clean" if not compiled else ", ".join(compiled[:10])))

    try:
        pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
        ok = "**/*.md" in pyproject
        checks.append(
            AuditCheck(
                "persona-packaging",
                ok,
                "agents Markdown package data configured" if ok else "agents Markdown package data missing",
            )
        )
    except OSError as exc:
        checks.append(AuditCheck("persona-packaging", False, str(exc)))

    return tuple(checks)


def audit_summary(root: str | Path) -> dict[str, object]:
    checks = audit_repository(root)
    return {
        "ok": all(check.ok for check in checks),
        "checks": [check.as_dict() for check in checks],
    }
