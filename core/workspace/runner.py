"""Deterministic Git execution boundary for Phase 58."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol


class GitError(RuntimeError):
    """Git operation failed or violated the lifecycle boundary."""


class GitRunner(Protocol):
    """Application-provided execution boundary.

    The workspace authority never constructs shell commands itself. A host adapter
    supplies a pre-authorized callable that maps argv + cwd to bounded text.
    """

    def run(self, args: list[str], *, cwd: Path) -> str: ...


@dataclass(frozen=True, slots=True)
class CallableGitRunner:
    executor: Callable[[list[str], Path], str]

    def run(self, args: list[str], *, cwd: Path) -> str:
        if not args or args[0] != "git":
            raise GitError("only the git executable is permitted")
        if any("\x00" in value for value in args):
            raise GitError("NUL is not allowed in Git arguments")
        try:
            result = self.executor(list(args), cwd)
        except Exception as exc:
            raise GitError("Git execution failed") from exc
        if not isinstance(result, str):
            raise GitError("Git executor must return text")
        if len(result.encode("utf-8")) > 2 * 1024 * 1024:
            raise GitError("Git output exceeds the safety limit")
        return result


class InMemoryGitRunner:
    """Deterministic test double that records all invocations."""

    def __init__(self) -> None:
        self.calls: list[tuple[tuple[str, ...], str]] = []
        self.responses: dict[tuple[str, ...], str] = {}

    def set(self, args: list[str], response: str = "") -> None:
        self.responses[tuple(args)] = response

    def run(self, args: list[str], *, cwd: Path) -> str:
        self.calls.append((tuple(args), str(cwd)))
        try:
            return self.responses[tuple(args)]
        except KeyError as exc:
            raise GitError(f"no fake response for {args}") from exc
