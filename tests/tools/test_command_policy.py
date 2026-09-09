import pytest

from tools.sandbox.command_policy import CommandPolicy, CommandPolicyError


def test_policy_allows_normal_command() -> None:
    CommandPolicy().check("python -m pytest")


def test_policy_blocks_destructive_command() -> None:
    with pytest.raises(CommandPolicyError, match="blocked"):
        CommandPolicy().check("rm -rf /")


def test_policy_rejects_empty_command() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        CommandPolicy().check("   ")
