"""Repository-neutral provenance and external-branding hygiene checks."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

# Digest-only denylist: the source repository does not retain external project names.
_FORBIDDEN_DIGESTS = frozenset({
    "2f7875656a69466cfdff4d57082ce7bbb1ef49284e5b5d26de2d0e0662e0ba31",
    "a32b469a30ed484031860b2573f3a283f3a077fe50d210be4a6d42f7f301aea5",
})
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")


def contains_forbidden_branding(text: str) -> bool:
    tokens = _TOKEN_RE.findall(text.lower())
    for token in tokens:
        if hashlib.sha256(token.encode()).hexdigest() in _FORBIDDEN_DIGESTS:
            return True
    for index in range(len(tokens) - 1):
        phrase = f"{tokens[index]} {tokens[index + 1]}"
        if hashlib.sha256(phrase.encode()).hexdigest() in _FORBIDDEN_DIGESTS:
            return True
    return False


def scan_text_files(root: str | Path, suffixes: frozenset[str]) -> list[str]:
    root = Path(root).resolve()
    findings: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in suffixes:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if contains_forbidden_branding(text):
            findings.append(str(path.relative_to(root)))
    return sorted(findings)
