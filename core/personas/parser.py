from __future__ import annotations

# isort: skip_file

import re
from pathlib import Path

from core.personas.models import AgentPersona


_REQUIRED_SECTIONS = (
    "Identity", "Personality", "Core Mission", "Expertise", "Responsibilities", "Workflow",
    "Critical Rules", "Boundaries", "Deliverables", "Failure Behavior", "Escalation Behavior",
    "Verification Expectations", "Evidence Requirements",
)
_ALLOWED_FRONTMATTER = {"schema", "version", "id", "name", "division", "description"}
_FORBIDDEN_FRONTMATTER = {
    "capabilities", "permissions", "harnesses", "environments", "tools", "commands",
    "exec", "execute", "shell", "network", "credentials", "secrets",
}
_KEY_RE = re.compile(r"^[a-z][a-z0-9_-]*$")


def parse_persona(text: str, *, source_path: str | None = None) -> AgentPersona:
    if not isinstance(text, str):
        raise TypeError("Persona source must be text")
    frontmatter, body = _split_frontmatter(text)
    _reject_unknown_or_dangerous(frontmatter)
    required = ("schema", "version", "id", "name", "division", "description")
    missing = [key for key in required if key not in frontmatter]
    if missing:
        raise ValueError("Persona frontmatter missing: " + ", ".join(missing))
    sections = _parse_sections(body)
    missing_sections = [name for name in _REQUIRED_SECTIONS if name not in sections]
    if missing_sections:
        raise ValueError("Persona sections missing: " + ", ".join(missing_sections))
    return AgentPersona(
        schema=frontmatter["schema"], version=_parse_int(frontmatter["version"], "version"),
        id=frontmatter["id"], name=frontmatter["name"], division=frontmatter["division"],
        description=frontmatter["description"], identity=_scalar(sections["Identity"]),
        personality=_scalar(sections["Personality"]), mission=_scalar(sections["Core Mission"]),
        expertise=_items(sections["Expertise"]), responsibilities=_items(sections["Responsibilities"]),
        workflow=_items(sections["Workflow"]), critical_rules=_items(sections["Critical Rules"]),
        boundaries=_items(sections["Boundaries"]), deliverables=_items(sections["Deliverables"]),
        failure_behavior=_items(sections["Failure Behavior"]),
        escalation_behavior=_items(sections["Escalation Behavior"]),
        verification_expectations=_items(sections["Verification Expectations"]),
        evidence_requirements=_items(sections["Evidence Requirements"]), source_path=source_path,
    )


def parse_persona_file(path: str | Path) -> AgentPersona:
    path = Path(path)
    return parse_persona(path.read_text(encoding="utf-8"), source_path=str(path))


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("Persona must start with YAML-style frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("Persona frontmatter is not terminated") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line or line[: len(line) - len(line.lstrip())]:
            raise ValueError(f"Invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not _KEY_RE.fullmatch(key):
            raise ValueError(f"Invalid frontmatter key: {key!r}")
        if key in values:
            raise ValueError(f"Duplicate frontmatter key: {key}")
        value = value.strip()
        if not value:
            raise ValueError(f"Empty frontmatter value: {key}")
        if value[0:1] in {"'", '"'}:
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f"Unterminated frontmatter value: {key}")
            value = value[1:-1]
        values[key] = value
    return values, "\n".join(lines[end + 1 :]).strip() + "\n"


def _parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    chunks: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                _store_section(sections, current, chunks)
            current = line[3:].strip()
            chunks = []
        elif current is not None:
            chunks.append(line)
        elif line.strip() and not line.startswith("#"):
            raise ValueError("Content before the first persona section is not allowed")
    if current is not None:
        _store_section(sections, current, chunks)
    return sections


def _store_section(sections: dict[str, str], name: str, chunks: list[str]) -> None:
    if name in sections:
        raise ValueError(f"Duplicate persona section: {name}")
    content = "\n".join(chunks).strip()
    if not content:
        raise ValueError(f"Empty persona section: {name}")
    sections[name] = content


def _scalar(content: str) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) != 1 or lines[0].startswith("-"):
        raise ValueError("Scalar persona sections must contain exactly one paragraph")
    return lines[0]


def _items(content: str) -> tuple[str, ...]:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Persona collection section cannot be empty")
    bullet_flags = [line.startswith("-") and line != "-" for line in lines]
    if any(bullet_flags) and not all(bullet_flags):
        raise ValueError("Persona collection sections cannot mix paragraphs and Markdown bullets")
    if not any(bullet_flags):
        if len(lines) != 1:
            raise ValueError("Persona collection sections must use Markdown bullet items for multiple entries")
        items = [lines[0]]
    else:
        items = [line[1:].strip() for line in lines]
    if any(not item for item in items):
        raise ValueError("Persona collection section contains an empty item")
    if len(items) != len(set(items)):
        raise ValueError("Persona collection section contains duplicate items")
    return tuple(items)


def _parse_int(value: str, name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Persona {name} must be an integer") from exc


def _reject_unknown_or_dangerous(frontmatter: dict[str, str]) -> None:
    dangerous = sorted(set(frontmatter) & _FORBIDDEN_FRONTMATTER)
    if dangerous:
        raise ValueError(
            "Persona cannot declare execution or privilege fields: " + ", ".join(dangerous)
        )
    unknown = sorted(set(frontmatter) - _ALLOWED_FRONTMATTER)
    if unknown:
        raise ValueError("Persona has unsupported frontmatter fields: " + ", ".join(unknown))
