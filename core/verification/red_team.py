from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class RedTeamStatus(str, Enum):
    RESISTED = "resisted"
    FOUND_FLAW = "found_flaw"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class RedTeamChallenge:
    name: str
    attack: Callable[[], bool] = field(repr=False, compare=False)
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Red-team challenge name must not be empty")


@dataclass(frozen=True)
class RedTeamResult:
    challenge_id: str
    name: str
    status: RedTeamStatus
    details: str = ""


class RedTeamSuite:
    """Attempts to falsify a result; any successful attack is a verification failure."""

    def __init__(self, challenges: tuple[RedTeamChallenge, ...] = ()) -> None:
        self._challenges: list[RedTeamChallenge] = list(challenges)

    def add(self, challenge: RedTeamChallenge) -> RedTeamChallenge:
        if any(item.id == challenge.id for item in self._challenges):
            raise ValueError(f"Duplicate red-team challenge ID: {challenge.id}")
        if any(item.name == challenge.name for item in self._challenges):
            raise ValueError(f"Duplicate red-team challenge name: {challenge.name}")
        self._challenges.append(challenge)
        return challenge

    def run(self) -> tuple[RedTeamResult, ...]:
        results: list[RedTeamResult] = []
        for challenge in self._challenges:
            try:
                flaw_found = bool(challenge.attack())
            except Exception as exc:  # noqa: BLE001 - attack failures are flaws.
                results.append(
                    RedTeamResult(
                        challenge.id,
                        challenge.name,
                        RedTeamStatus.FOUND_FLAW,
                        f"attack raised: {exc}",
                    )
                )
                continue
            results.append(
                RedTeamResult(
                    challenge.id,
                    challenge.name,
                    RedTeamStatus.FOUND_FLAW if flaw_found else RedTeamStatus.RESISTED,
                    "attack found a flaw" if flaw_found else "attack did not falsify the result",
                )
            )
        return tuple(results)

    @staticmethod
    def passed(results: tuple[RedTeamResult, ...]) -> bool:
        return bool(results) and all(item.status is RedTeamStatus.RESISTED for item in results)
