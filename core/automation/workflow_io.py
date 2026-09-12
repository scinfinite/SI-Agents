"""Portable, validated import/export helpers for Phase 65 workflow definitions."""
from __future__ import annotations

import json
from pathlib import Path

from .workflows import WorkflowDefinition, _definition_from_dict

_MAX_EXPORT_BYTES = 256 * 1024


def export_definition(definition: WorkflowDefinition, path: str | Path | None = None) -> str:
    """Return a canonical JSON definition and optionally write it atomically."""
    encoded = json.dumps(definition.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if len(encoded.encode("utf-8")) > _MAX_EXPORT_BYTES:
        raise ValueError("workflow definition exceeds export limit")
    if path is not None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(encoded + "\n", encoding="utf-8")
        temporary.replace(target)
    return encoded


def import_definition(source: str | bytes | Path) -> WorkflowDefinition:
    """Parse, validate, and return a workflow definition from JSON text or a file."""
    if isinstance(source, Path):
        raw_text = source.read_text(encoding="utf-8")
    elif isinstance(source, bytes):
        raw_text = source.decode("utf-8")
    else:
        raw_text = source
    if len(raw_text.encode("utf-8")) > _MAX_EXPORT_BYTES:
        raise ValueError("workflow definition exceeds import limit")
    try:
        raw = json.loads(raw_text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("workflow definition must be valid UTF-8 JSON") from exc
    if not isinstance(raw, dict):
        raise ValueError("workflow definition must be a JSON object")
    return _definition_from_dict(raw)
