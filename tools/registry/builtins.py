from __future__ import annotations

from tools.registry.registry import ToolDescriptor, ToolRegistry, ToolStatus


def register_builtin_tools(registry: ToolRegistry) -> None:
    """Register tool capabilities without implying that any permission is granted."""
    definitions = (
        ("filesystem", "filesystem", "Workspace-scoped file operations", ("filesystem_read",)),
        ("terminal", "terminal", "Policy-gated local command execution", ("local_command",)),
        ("git", "git", "Repository inspection and source-control operations", ("repository_read",)),
        ("github", "github", "GitHub API and repository inspection", ("github_read",)),
        ("web", "web", "HTTP retrieval for research", ("web_read",)),
        ("code_search", "code_analysis", "Workspace source search", ("repository_read",)),
        ("python_parser", "code_analysis", "Python AST parsing", ("repository_read",)),
        ("compiler", "build", "Compiler and syntax verification commands", ("local_command",)),
        ("linter", "quality", "Static analysis commands", ("local_command",)),
        ("formatter", "quality", "Formatting and formatting checks", ("local_command",)),
        ("test_runner", "testing", "Automated test execution", ("local_command",)),
        ("package_manager", "dependencies", "Package-manager verification commands", ("local_command",)),
        ("container", "sandbox", "Isolated container execution", ("isolated_execution",)),
        ("artifact", "artifacts", "Artifact storage and metadata", ("workspace_write",)),
    )
    for name, category, description, permissions in definitions:
        registry.register(
            ToolDescriptor(
                name=name,
                category=category,
                status=ToolStatus.EXPERIMENTAL,
                description=description,
                permissions=permissions,
                verification=("registry registration",),
            )
        )
