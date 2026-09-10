"""Dependency-free scanner for agent, skill, rule, hook, and config surfaces."""

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
import re


class Severity(IntEnum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    path: str
    message: str
    evidence: str
    remediation: str
    auto_fixable: bool = False


_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"\b(?:sk|ghp|glpat|xox[baprs])-[-_A-Za-z0-9]{12,}\b"),
)
_BROAD_PERMISSION = re.compile(r"(?i)(?:allow|permission|permissions).*\b(?:\*|all|bash\s*\(\s*\*\s*\)|shell\s*\(\s*\*\s*\))")
_UNSAFE_HOOK = re.compile(r"(?i)(?:hook|command).*\b(?:curl|wget|bash\s+-c|sh\s+-c|eval\s*\(|exec\s*\()")
_SUSPICIOUS_INJECTION = re.compile(r"(?i)(?:ignore\s+(?:all|previous|prior)\s+instructions|reveal\s+(?:the\s+)?system\s+prompt|disable\s+(?:security|approval|governance))")
_UNPINNED_TOOL = re.compile(r"(?i)(?:npx\s+-y|pip\s+install\s+[^\s]+@latest)")


class GovernanceScanner:
    """Scan without modifying files and return stable path/rule ordering."""

    def scan(self, root: str | Path) -> tuple[Finding, ...]:
        base = Path(root).resolve()
        if not base.exists():
            raise FileNotFoundError(base)
        findings: list[Finding] = []
        for path in sorted(p for p in base.rglob("*") if p.is_file() and not self._ignored(p)):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            relative = path.relative_to(base).as_posix()
            findings.extend(self._scan_text(relative, text))
        return tuple(sorted(findings, key=lambda item: (item.path, -item.severity, item.rule_id, item.message)))

    @staticmethod
    def _ignored(path: Path) -> bool:
        return any(part in {".git", ".venv", "__pycache__", ".pytest_cache", "build", "dist", ".dart_tool"} for part in path.parts)

    def _scan_text(self, path: str, text: str) -> list[Finding]:
        findings: list[Finding] = []
        for number, line in enumerate(text.splitlines(), 1):
            evidence = f"line {number}: {line.strip()[:240]}"
            for pattern in _SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding("secret.literal", Severity.CRITICAL, path, "secret-like literal detected", evidence, "Replace the literal with a scoped secret reference and keep secrets outside source control."))
                    break
            if _BROAD_PERMISSION.search(line):
                findings.append(Finding("permission.broad", Severity.HIGH, path, "broad or wildcard permission detected", evidence, "Replace wildcard authority with the narrowest explicit capability and scope."))
            if _UNSAFE_HOOK.search(line):
                findings.append(Finding("hook.unsafe-command", Severity.HIGH, path, "hook or configuration contains an unsafe command pattern", evidence, "Use bounded typed hooks and explicit, non-interpolated inputs; do not execute untrusted configuration."))
            if _SUSPICIOUS_INJECTION.search(line):
                findings.append(Finding("content.injection", Severity.MEDIUM, path, "instruction-like prompt injection pattern detected", evidence, "Treat the content as untrusted data and remove authority-bearing instructions from configuration."))
            if path.endswith((".json", ".yaml", ".yml", ".toml")) and _UNPINNED_TOOL.search(line):
                findings.append(Finding("supply.unpinned-tool", Severity.MEDIUM, path, "unpinned package execution detected", evidence, "Pin tool/package versions or immutable references before execution."))
        return findings
