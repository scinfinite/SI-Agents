from __future__ import annotations

from core.capacity import CapacityLevel, CapacityPolicy, CapacityTarget


def test_capacity_levels_classify_and_bound_termux() -> None:
    policy = CapacityPolicy()
    assert policy.classify({"action": "status"}) is CapacityLevel.LOW
    assert policy.classify({"action": "run-tests"}) is CapacityLevel.MEDIUM
    assert policy.classify({"action": "compile-java-project"}) is CapacityLevel.HIGH

    low = policy.evaluate({"action": "status"}, target=CapacityTarget.TERMUX)
    medium = policy.evaluate({"action": "run-tests"}, target=CapacityTarget.TERMUX)
    high = policy.evaluate({"action": "compile-java-project"}, target=CapacityTarget.TERMUX)

    assert low.allowed and low.max_workers == 1
    assert medium.allowed and medium.max_workers == 2
    assert not high.allowed and not high.compile_allowed


def test_capacity_allows_high_work_on_codespace_and_desktop() -> None:
    policy = CapacityPolicy()
    for target in (CapacityTarget.DESKTOP, CapacityTarget.CODESPACE):
        decision = policy.evaluate({"action": "compile"}, target=target)
        assert decision.allowed
        assert decision.compile_allowed
        assert decision.max_workers >= 4
