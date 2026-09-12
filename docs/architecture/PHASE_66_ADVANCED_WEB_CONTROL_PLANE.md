# Phase 66 — Advanced Web Control Plane

## Status

**Implementation active.** Phase 65 is closed on `main`; Phase 66 is the active V4 phase and remains open until the final exact-tree `main` CI gate is green.

## Objective

Provide a secure, accessible, same-origin web control plane over the existing SI Control API. The web surface is an observation and authorized-control client; it is never a second state or authorization authority.

## Delivered contract

The Phase 66 web surface provides:

- responsive operational overview and health state;
- live activity/event inspection with bounded polling;
- workflow and run views;
- accessible text topology/DAG representation;
- evidence and control-plane evidence views;
- identity-bound human approval queue visibility;
- environment/resource and settings views;
- repository code/Markdown/JSON inspection, bounded search, and latest-commit diff viewing;
- same-origin API reuse rather than an independent backend;
- keyboard navigation, skip link, semantic landmarks, status announcements, and non-color-only state labels;
- restrictive Content Security Policy and `nosniff` response headers;
- inherited WebServer authentication and audit behavior;
- safe static/repository path resolution with traversal rejection;
- bounded source/diff payloads and repository search traversal;
- no inline script, inline style, remote font, telemetry, or third-party runtime dependency.

## Architecture

`core/web/advanced.py` extends the existing `WebServer` rather than introducing a competing web authority. `create_advanced_server()` installs `AdvancedWebRequestHandler` on the existing HTTP server configuration, preserving the established authentication, audit, Control API, SSE, WebSocket, and governance boundaries.

`web/control/` contains the dependency-free browser surface. `core/control_api/openapi.py` documents the inspection endpoints. The browser talks only to same-origin `/api/v1/...` routes and does not execute agents, tools, workflows, or provider calls locally.

## Authority and security

The UI never directly executes agents, tools, workflows, or provider calls. Mutations go through the versioned Control API and therefore remain subject to SI Core governance. Identity-bound approval routes require the existing identity headers; the browser does not invent an identity. Remote exposure remains governed by the existing WebServer configuration and authentication boundary.

Repository inspection is read-only. It rejects `.git` paths, traversal outside the repository root, unsupported file types, oversized source/diff responses, and oversized search queries. Repository search stops after a fixed file budget. Git diff uses an argument-vector subprocess with a two-second timeout and no shell.

The browser refresh loop is deliberately bounded and disposable. SSE/WebSocket remain available through the existing API for clients that need streaming; the dashboard uses bounded polling so a disconnected tab cannot consume an unbounded server-side stream.

## Information architecture

1. **Overview** — system counts, health, and snapshot.
2. **Live activity** — searchable event stream.
3. **Workflows** — workflow definitions and runs.
4. **Topology** — nodes/edges and dependency relationships with an accessible textual fallback.
5. **Evidence** — control-plane evidence summary.
6. **Approvals** — identity-bound human approval queue.
7. **Repository** — bounded code/Markdown/JSON source, search, and diff inspection.
8. **Resources** — runtime/environment information.
9. **Settings** — API/security/execution posture.

## Verification

Acceptance tests are in `tests/unit/test_phase66_web_control.py` and `tests/unit/test_phase66_advanced_web.py`. They verify same-origin UI delivery, API reuse, inherited authentication, security headers, remote-binding policy, repository source/search/diff bounds, `.git` exclusion, and static traversal protection. Repository-wide CI additionally verifies build/distribution, wheel installation, repository audit, integration verification, Ruff, compileall, and the complete pytest suite.

## Closure rule

Phase 66 is complete only after implementation, security/accessibility tests, repository-wide validation, documentation synchronization, and final exact-tree `main` CI are green. No Phase 66 completion claim is valid before that final gate.
