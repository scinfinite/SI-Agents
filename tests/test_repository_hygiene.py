from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ("Agency" + " Agents", "agency" + "-agents", "E" + "CC")
TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".yml", ".yaml", ".txt"}


def test_shipped_repository_has_no_external_project_branding() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert not any(term in text for term in FORBIDDEN), path


def test_temporary_phase29_artifacts_are_absent() -> None:
    forbidden_names = {
        "agency" + "-agents" + "-parity.json",
        "agency" + "_agents" + "_audit.py",
        "PHASE_29_" + "AGENCY_" + "AGENTS_AUDIT.md",
        "persona_parity_build.py",
        "phase29_unique_names.py",
        "phase29_heading_fix.py",
        "phase29_list_fix.py",
        "phase29-test-debug.txt",
    }
    for path in ROOT.rglob("*"):
        if path.is_file() and path.name in forbidden_names:
            raise AssertionError(path)
