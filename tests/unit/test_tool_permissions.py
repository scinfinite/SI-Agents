from core.policies.permission_engine import PermissionDecision, PermissionEngine, PermissionScope


def test_phase_two_external_and_isolated_permissions_are_explicit() -> None:
    engine = PermissionEngine()
    assert engine.decide("github_read") is PermissionDecision.ALLOW
    assert engine.decide("web_read") is PermissionDecision.ALLOW
    assert engine.decide("isolated_execution") is PermissionDecision.ALLOW


def test_scoped_tool_permissions_do_not_leak_to_other_tools() -> None:
    engine = PermissionEngine(
        scopes=(PermissionScope(agent="researcher", tool="web", capabilities=frozenset({"web_read"})),)
    )
    assert engine.decide("web_read", agent="researcher", tool="web") is PermissionDecision.ALLOW
    assert engine.decide("local_command", agent="researcher", tool="web") is PermissionDecision.DENY
    assert engine.decide("web_read", agent="developer", tool="web") is PermissionDecision.DENY
