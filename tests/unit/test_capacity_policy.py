from __future__ import annotations

import pytest

from core.capacity import CapacityLevel, CapacityPolicy


def test_termux_low_allows_one_or_two_workers() -> None:
    policy = CapacityPolicy(environment="termux")
    assert policy.decide(CapacityLevel.LOW, workers=1).allowed
    assert policy.decide(CapacityLevel.LOW, workers=2).workers == 2
    with pytest.raises(ValueError):
        policy.decide(CapacityLevel.LOW, workers=3)


def test_termux_medium_allows_three_to_five_workers() -> None:
    policy = CapacityPolicy(environment="termux")
    assert policy.decide(CapacityLevel.MEDIUM, workers=3).allowed
    assert policy.decide(CapacityLevel.MEDIUM, workers=5).workers == 5
    with pytest.raises(ValueError):
        policy.decide(CapacityLevel.MEDIUM, workers=2)
    with pytest.raises(ValueError):
        policy.decide(CapacityLevel.MEDIUM, workers=6)


def test_termux_high_and_build_work_are_remote_only() -> None:
    policy = CapacityPolicy(environment="termux")
    high = policy.decide(CapacityLevel.HIGH, workers=8)
    build = policy.decide(CapacityLevel.MEDIUM, workers=5, workload="compile the project")
    assert not high.allowed and high.requires_remote
    assert not build.allowed and build.requires_remote


def test_desktop_high_is_allowed_with_warning() -> None:
    decision = CapacityPolicy(environment="desktop").decide(CapacityLevel.HIGH, workers=8)
    assert decision.allowed
    assert decision.warning
