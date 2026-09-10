from pathlib import Path

import pytest

from tools.sandbox.docker_sandbox import DockerSandbox


def test_docker_sandbox_builds_restricted_argv(tmp_path) -> None:
    sandbox = DockerSandbox(tmp_path)

    argv = sandbox._argv("python -c 'print(42)'")

    assert argv[:3] == ["docker", "run", "--rm"]
    assert "--network=none" in argv
    assert "--read-only" in argv
    assert "--cap-drop=ALL" in argv
    assert "--security-opt=no-new-privileges" in argv
    assert "--memory=512m" in argv
    assert "--cpus=1.0" in argv
    assert "--pids-limit=256" in argv
    assert "--workdir=/workspace" in argv
    assert argv[-3:] == ["/bin/sh", "-lc", "python -c 'print(42)'"]
    mount = next(value for value in argv if value.startswith("--mount=type=bind"))
    assert f"src={Path(tmp_path).resolve()}" in mount
    assert "dst=/workspace,rw" in mount


def test_docker_sandbox_rejects_invalid_configuration(tmp_path) -> None:
    with pytest.raises(ValueError, match="image"):
        DockerSandbox(tmp_path, image=" ")
    with pytest.raises(ValueError, match="PID"):
        DockerSandbox(tmp_path, pids_limit=0)


def test_docker_sandbox_rejects_empty_command(tmp_path) -> None:
    sandbox = DockerSandbox(tmp_path)

    with pytest.raises(ValueError, match="Command"):
        sandbox._argv(" ")
