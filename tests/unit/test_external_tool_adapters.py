from __future__ import annotations

from types import SimpleNamespace
from typing import ClassVar

from tools.registry.container import ContainerTool
from tools.registry.github import GitHubTool
from tools.registry.web import WebToolImpl


class FakeResponse:
    headers: ClassVar[dict[str, str]] = {"Content-Type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return b'{"ok": true}'


class FakeBackend:
    workspace = "/tmp/workspace"

    def run(self, command: str, *, timeout: float):
        assert command == "echo ok"
        assert timeout == 5
        return SimpleNamespace(succeeded=True, stdout="ok\n", stderr="")


def test_web_and_github_adapters_use_untrusted_response_data(monkeypatch) -> None:
    monkeypatch.setattr("urllib.request.urlopen", lambda *_args, **_kwargs: FakeResponse())
    web = WebToolImpl()
    assert web.fetch("https://example.invalid").succeeded
    result = GitHubTool(token="secret-not-logged").fetch("https://api.github.com/repos/example/project")
    assert result.succeeded
    assert '"ok": true' in result.value


def test_container_adapter_delegates_to_isolated_backend() -> None:
    result = ContainerTool(FakeBackend()).run("echo ok", timeout=5)
    assert result.succeeded
    assert result.value == "ok\n"
