# Phase 66 — Advanced Web Control Plane

## Status

**Complete / 100% — fully closed on `main`.** Phase 65 was closed on `main` before Phase 66 began. Phase 66 implementation was merged as PR #79. The final synchronized documentation tree was then validated by mainline CI #1280 / run `34699748468` on commit `89e59f31c5785ab7a29aab8eec927cbebaa3b383`, which completed successfully. This is the authoritative final closure evidence.

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
- governed run-request controls that submit through the existing Control API with explicit action, subject, capabilities, and idempotency key;
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

The UI never directly executes agents, tools, workflows, or provider calls. Governed run requests are ordinary Control API requests and therefore remain subject to SI Core authorization; the browser cannot bypass capability checks. Identity-bound approval routes require the existing identity headers; the browser does not invent an identity. Remote exposure remains governed by the existing WebServer configuration and authentication boundary.

Repository inspection is read-only. It rejects `.git` paths, traversal outside the repository root, unsupported file types, oversized source/diff responses, and oversized search queries. Repository search stops after a fixed file budget. Git diff uses an argument-vector subprocess with a two-second timeout and no shell.

The browser refresh loop is deliberately bounded and disposable. SSE/WebSocket remain available through the existing API for clients that need streaming; the dashboard uses bounded polling so a disconnected tab cannot consume an unbounded server-side stream.

## Information architecture

1. **Overview** — system counts, health, and snapshot.
2. **Live activity** — searchable event stream.
3. **Workflows** — workflow definitions and runs.
4. **Topology** — nodes/edges and dependency relationships with an accessible textual fallback.
5. **Evidence** — control-plane evidence summary.
6. **Approvals** — identity-bound human approval queue.
7. **Controls** — governed run-request submission through the Control API.
8. **Repository** — bounded code/Markdown/JSON source, search, and diff inspection.
9. **Resources** — runtime/environment information.
10. **Settings** — API/security/execution posture.

## Verification

PR #79 implementation/closure CI #1275 / `34699632473` passed the implementation closure suite. The final synchronized-tree mainline CI #1280 / `34699748468` on the final documentation state completed successfully. The SDK workflow on the same final commit also completed successfully as run `34699748479`.

Acceptance tests are in `tests/unit/test_phase66_web_control.py` and `tests/unit/test_phase66_advanced_web.py`.

## Closure rule

Phase 66 is complete only when the implementation, security/accessibility tests, repository-wide validation, documentation synchronization, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree `main` CI are green. **All required gates are now green; Phase 66 is fully closed at 100%.**
