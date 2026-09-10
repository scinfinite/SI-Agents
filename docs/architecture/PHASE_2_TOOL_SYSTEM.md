# Phase 2 — Tool System

## Objective

Provide SI-Agents with a controlled, discoverable tool layer for filesystem work, source control, research, code analysis, build/test tooling, containers, and artifacts.

## Implemented

- Tool descriptor model and lifecycle status.
- Tool registry with duplicate protection and category/status lookup.
- Standard tool catalog covering filesystem, terminal, Git, GitHub, web, code search, Python parsing, compiler, linter, formatter, test runner, package manager, container, and artifact storage.
- Workspace-scoped filesystem access with traversal protection.
- Read-oriented Git adapter; repository mutations must go through an approved command executor.
- GitHub HTTP adapter with optional injected token; credentials are never generated or logged by the adapter.
- HTTP research adapter with explicit timeout and untrusted-content boundary.
- Regex source search and Python AST parsing.
- Reusable developer command adapters for compilation, Ruff lint/format checks, pytest, and pip dependency checks.
- Container adapter around the existing Docker isolation backend.
- Artifact storage with metadata and atomic metadata writes.
- Tool registry integration into the orchestrator.
- Tool executor that binds implementations to registered descriptors and enforces descriptor permissions before invocation.
- Explicit permission capabilities for GitHub reads, web reads, and isolated execution.
- Unit coverage for registry invariants, workspace boundaries, Git mutation blocking, developer tooling, artifacts, external adapters, permissions, tool execution, and orchestrator integration.

## Security boundaries

Tool registration and capability selection never grant permission. Execution remains behind the control-plane permission and approval gates.

Local execution is a trusted development backend, not a security boundary. Untrusted code must use an isolated backend such as the Docker sandbox, subject to the Docker daemon trust boundary.

Remote web/GitHub content is treated as untrusted data and must not be interpreted as system instructions.

The Git adapter intentionally blocks repository-mutating commands. Approved mutation can be performed later through the existing command/approval path.

## Verification

The repository CI pipeline must pass project installation, distribution build, Ruff, and the complete pytest suite before Phase 2 is marked complete.

Some tools remain `experimental` in the registry because their real-world availability depends on the host environment or external service. This status is about tool validation, not whether the Phase 2 architecture exists.

## Explicit non-goals

Phase 2 does not implement the engineering brain, autonomous agent reasoning, model routing, distributed execution, or self-improvement. Those belong to later phases.
