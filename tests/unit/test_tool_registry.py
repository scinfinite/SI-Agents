from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from tools.registry.artifacts import ArtifactStore
from tools.registry.builtins import register_builtin_tools
from tools.registry.code_search import CodeSearchTool
from tools.registry.command_tools import (
    CompilerTool,
    FormatterTool,
    LinterTool,
    PackageManagerTool,
    TestRunnerTool,
)
from tools.registry.filesystem import FileSystemToolImpl
from tools.registry.git import GitTool
from tools.registry.python_parser import PythonParserTool
from tools.registry.registry import ToolDescriptor, ToolRegistry, ToolStatus


def test_registry_rejects_duplicates_and_invalid_validated_tools() -> None:
    registry = ToolRegistry()
    registry.register(ToolDescriptor("one", "test"))
    try:
        registry.register(ToolDescriptor("one", "test"))
        raise AssertionError("duplicate name was accepted")
    except ValueError as exc:
        assert "Duplicate tool name" in str(exc)
    try:
        ToolDescriptor("bad", "test", status=ToolStatus.VALIDATED)
        raise AssertionError("validated tool without verification was accepted")
    except ValueError as exc:
        assert "verification" in str(exc)


def test_builtin_registry_covers_phase_two_categories() -> None:
    registry = ToolRegistry()
    register_builtin_tools(registry)
    names = {tool.name for tool in registry.all()}
    assert names == {
        "filesystem", "terminal", "git", "github", "web", "code_search", "python_parser",
        "compiler", "linter", "formatter", "test_runner", "package_manager", "container", "artifact",
    }
    assert all(tool.status is ToolStatus.EXPERIMENTAL for tool in registry.all())
    assert all(tool.verification for tool in registry.all())


def test_filesystem_and_code_tools_stay_inside_workspace() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        tool = FileSystemToolImpl(root)
        tool.write_text("app.py", "answer = 42\n")
        assert tool.read_text("app.py") == "answer = 42\n"
        assert tool.list() == ("app.py",)
        assert tool.exists("app.py")
        assert "answer = 42" in CodeSearchTool(root).search("answer").value
        assert PythonParserTool(root).parse("app.py").succeeded
        try:
            tool.read_text("../outside")
            raise AssertionError("workspace traversal was accepted")
        except PermissionError:
            pass


def test_git_and_developer_tool_adapters_return_results() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        assert subprocess.run(["git", "init", "-q", str(root)], check=False).returncode == 0
        assert GitTool(root).status().succeeded
        assert not GitTool(root).run(("commit", "--allow-empty", "-m", "blocked")).succeeded
        Path(root / "app.py").write_text("answer = 42\n", encoding="utf-8")
        assert TestRunnerTool(root).available("python")
        assert CompilerTool(root).python_compile("app.py").succeeded
        assert LinterTool(root).ruff("check", "app.py").succeeded
        assert FormatterTool(root).ruff_format_check("app.py").succeeded
        assert PackageManagerTool(root).pip_check().succeeded


def test_artifact_store_persists_metadata() -> None:
    with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
        source_path = Path(source) / "result.txt"
        source_path.write_text("evidence", encoding="utf-8")
        store = ArtifactStore(destination)
        artifact_id = store.put(source_path)
        metadata = store.get_metadata(artifact_id)
        assert metadata["id"] == artifact_id
        assert Path(metadata["path"]).read_text(encoding="utf-8") == "evidence"
