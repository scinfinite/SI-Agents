from __future__ import annotations

import re
from pathlib import Path

from core.skills.models import Skill, SkillRequirement, SkillStatus

_REQUIRED = (
    "Purpose", "Inputs", "Outputs", "Prerequisites", "Workflow", "Tools",
    "Capabilities", "Permissions", "Verification", "Failure Behavior",
    "Evidence Requirements", "Examples", "Compatibility", "Provenance",
)
_ALLOWED = {"schema", "version", "id", "name", "category", "status", "dependencies"}
_FORBIDDEN = {"commands", "shell", "exec", "execute", "credentials", "secrets", "network", "install"}
_KEY = re.compile(r"^[a-z][a-z0-9_-]*$")


def parse_skill(text: str, *, source_path: str | None = None) -> Skill:
    if not isinstance(text, str):
        raise TypeError("Skill source must be text")
    meta, body = _frontmatter(text)
    unknown = sorted(set(meta) - _ALLOWED)
    dangerous = sorted(set(meta) & _FORBIDDEN)
    if dangerous:
        raise ValueError("Skill cannot declare execution or privilege fields: " + ", ".join(dangerous))
    if unknown:
        raise ValueError("Unsupported Skill frontmatter: " + ", ".join(unknown))
    missing = [key for key in ("schema", "version", "id", "name", "category", "status") if key not in meta]
    if missing:
        raise ValueError("Skill frontmatter missing: " + ", ".join(missing))
    sections = _sections(body)
    missing_sections = [name for name in _REQUIRED if name not in sections]
    if missing_sections:
        raise ValueError("Skill sections missing: " + ", ".join(missing_sections))
    return Skill(
        schema=meta["schema"], version=meta["version"], id=meta["id"], name=meta["name"],
        category=meta["category"], purpose=_scalar(sections["Purpose"]),
        inputs=_items(sections["Inputs"]), outputs=_items(sections["Outputs"]),
        prerequisites=_items(sections["Prerequisites"]), procedure=_items(sections["Workflow"]),
        required_tools=_items(sections["Tools"]), requested_capabilities=_items(sections["Capabilities"]),
        requested_permissions=_items(sections["Permissions"]), verification=_items(sections["Verification"]),
        failure_behavior=_items(sections["Failure Behavior"]), evidence_requirements=_items(sections["Evidence Requirements"]),
        examples=_items(sections["Examples"]), compatibility=_requirements(sections["Compatibility"]),
        provenance=_scalar(sections["Provenance"]), status=SkillStatus(meta["status"]),
        dependencies=_items(sections.get("Dependencies", "- none")),
    )


def parse_skill_file(path: str | Path) -> Skill:
    path = Path(path)
    return parse_skill(path.read_text(encoding="utf-8"), source_path=str(path))


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("Skill must start with frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("Skill frontmatter is not terminated") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line or line[:1].isspace():
            raise ValueError(f"Invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip().strip("\"'")
        if not _KEY.fullmatch(key) or not value:
            raise ValueError(f"Invalid frontmatter entry: {line!r}")
        if key in values:
            raise ValueError(f"Duplicate frontmatter key: {key}")
        values[key] = value
    return values, "\n".join(lines[end + 1:]).strip() + "\n"


def _sections(body: str) -> dict[str, str]:
    result: dict[str, str] = {}
    current = None
    chunks: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                _store(result, current, chunks)
            current, chunks = line[3:].strip(), []
        elif current is not None:
            chunks.append(line)
        elif line.strip() and not line.startswith("#"):
            raise ValueError("Content before first Skill section is not allowed")
    if current is not None:
        _store(result, current, chunks)
    return result


def _store(result: dict[str, str], name: str, chunks: list[str]) -> None:
    if name in result:
        raise ValueError(f"Duplicate Skill section: {name}")
    value = "\n".join(chunks).strip()
    if not value:
        raise ValueError(f"Empty Skill section: {name}")
    result[name] = value


def _scalar(value: str) -> str:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if len(lines) != 1:
        raise ValueError("Skill scalar sections must contain one paragraph")
    return lines[0]


def _items(value: str) -> tuple[str, ...]:
    items = tuple(line.strip()[1:].strip() for line in value.splitlines() if line.strip())
    if not items or any(not item for item in items) or any(not line.strip().startswith("-") for line in value.splitlines() if line.strip()):
        raise ValueError("Skill list sections must contain Markdown bullet items")
    if len(items) != len(set(items)):
        raise ValueError("Skill list section contains duplicate items")
    return items


def _requirements(value: str) -> tuple[SkillRequirement, ...]:
    rows = _items(value)
    result = []
    for row in rows:
        parts = [part.strip() for part in row.split("|", 2)]
        if len(parts) not in (2, 3) or not parts[0] or not parts[1]:
            raise ValueError("Compatibility items must be 'name | kind | version'")
        result.append(SkillRequirement(parts[0], parts[1], parts[2] if len(parts) == 3 else "*"))
    return tuple(result)
