from __future__ import annotations

from pathlib import Path

from core.legal.provenance import scan_text_files

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = frozenset({".md", ".json", ".py", ".toml", ".yml", ".yaml", ".txt"})


def test_shipped_repository_has_no_external_project_branding() -> None:
    assert scan_text_files(ROOT, TEXT_SUFFIXES) == []


def test_temporary_phase29_artifacts_are_absent() -> None:
    forbidden_names = {
        "persona_parity_build.py",
        "phase29_unique_names.py",
        "phase29_heading_fix.py",
        "phase29_list_fix.py",
        "phase29-test-debug.txt",
    }
    for path in ROOT.rglob("*"):
        if path.is_file() and ".ci-wheel-venv" not in path.parts and path.name in forbidden_names:
            raise AssertionError(path)
