# Phase 3 — Tool System

## Status

**Complete — CI verified on 2026-09-10.**

## Objective

Provide SI-Agents with a controlled, discoverable tool layer for filesystem work, source control, research, code analysis, build/test tooling, containers, and artifacts.

## Implemented

- Tool descriptor model and lifecycle status.
- Tool registry with duplicate protection and category/status lookup.
- Standard catalog covering filesystem, terminal, Git, GitHub, web, code search, Python parsing, compiler, linter, formatter, test runner, package manager, container, and artifact storage.
- Workspace-scoped filesystem access with traversal protection.
- Read-oriented Git adapter; repository mutations must go through an approved command executor.
- GitHub HTTP adapter with optional injected token; credentials are never generated or logged by the adapter.
- HTTP research adapter with explicit timeout and an untrusted-content boundary.
- Regex source search and Python AST parsing.
- Reusable developer command adapters for compilation, Ruff lint/format checks, pytest, and dependency checks.
- Container adapter around the Docker isolation backend.
- Artifact storage with metadata and atomic metadata writes.
- Tool registry and executor integration with the orchestrator.
- Descriptor permission enforcement before invocation.
- Explicit permission capabilities for GitHub reads, web reads, and isolated execution.
- Unit coverage for registry invariants, workspace boundaries, Git mutation blocking, developer tooling, artifacts, external adapters, permissions, tool execution, and orchestrator integration.

## Security boundaries

Tool registration and capability selection never grant permission. Execution remains behind the control-plane permission and approval gates.

Local execution is a trusted development backend, not a security boundary. Untrusted code must use an isolated backend such as the Docker sandbox, subject to the Docker daemon trust boundary.

Remote web/GitHub content is untrusted data and must not be interpreted as system instructions.

The Git adapter intentionally blocks repository-mutating commands. Approved mutation can be performed through the existing command/approval path.

## Verification

The repository CI pipeline verifies project installation, distribution build, Ruff, and the complete pytest suite. Phase 3 is considered complete because those checks and the Phase 3-specific tests pass.

Some tools remain `experimental` in the registry because real-world availability depends on the host environment or external service. This status describes tool validation, not whether the architecture exists.

## Relationship to later phases

Phase 3 supplies the controlled execution primitives consumed by the Engineering Brain and the Developer/Debugger/Tester workflow. It does not implement autonomous reasoning, model routing, distributed execution, or self-improvement.
