import pytest

from tools.sandbox.command_policy import CommandPolicyError
from tools.sandbox.local_sandbox import LocalSandbox


def test_run_captures_stdout_and_success(tmp_path) -> None:
    result = LocalSandbox(tmp_path).run("python -c \"print('hello')\"")

    assert result.succeeded
    assert result.return_code == 0
    assert result.stdout.strip() == "hello"
    assert result.stderr == ""


def test_run_captures_failure(tmp_path) -> None:
    result = LocalSandbox(tmp_path).run(
        "python -c \"import sys; print('bad', file=sys.stderr); sys.exit(3)\""
    )

    assert not result.succeeded
    assert result.return_code == 3
    assert result.stderr.strip() == "bad"


def test_run_reports_timeout(tmp_path) -> None:
    result = LocalSandbox(tmp_path).run(
        "python -c \"import time; time.sleep(1)\"", timeout=0.05
    )

    assert result.timed_out
    assert not result.succeeded


def test_run_blocks_destructive_command(tmp_path) -> None:
    with pytest.raises(CommandPolicyError, match="blocked"):
        LocalSandbox(tmp_path).run("rm -rf /")
