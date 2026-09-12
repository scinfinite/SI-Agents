# Phase 66 — Advanced Web Control Plane

## Status

**Implementation in progress.** Phase 65 is closed on `main`; Phase 66 is the active V4 phase.

## Objective

Provide a secure, accessible, same-origin web control plane over the existing versioned SI Control API. The web surface is an observation and authorized-control client; it is never a second state or authorization authority.

## Delivered contract

The Phase 66 web surface provides:

- responsive operational overview and health state;
- live activity/event inspection with bounded polling;
- workflow and run views;
- accessible text topology/DAG representation;
- evidence and control-plane evidence views;
- identity-bound human approval queue visibility;
- environment/resource and settings views;
- same-origin API reuse rather than an independent backend;
- keyboard navigation, skip link, semantic landmarks, status announcements, and non-color-only state labels;
- restrictive Content Security Policy and `nosniff` response headers;
- localhost-first binding inherited from the Control API;
- safe static path resolution with traversal rejection;
- no inline script, inline style, remote font, telemetry, or third-party runtime dependency.

## Authority and security

The UI never directly executes agents, tools, workflows, or provider calls. Mutations go through the versioned Control API and therefore remain subject to SI Core governance. Identity-bound approval routes require `X-SI-Subject` and `X-SI-Project`; the browser does not invent an identity. Remote binding remains explicitly rejected by the dependency-free development transport.

The browser refresh loop is deliberately bounded and disposable. SSE/WebSocket remain available through the existing API for clients that need streaming; the dashboard uses bounded polling so a disconnected tab cannot consume an unbounded server-side stream.

## Information architecture

1. **Overview** — system counts, health, and snapshot.
2. **Live activity** — searchable event stream.
3. **Workflows** — workflow definitions and runs.
4. **Topology** — nodes/edges and dependency relationships with an accessible textual fallback.
5. **Evidence** — control-plane evidence summary.
6. **Approvals** — identity-bound human approval queue.
7. **Resources** — runtime/environment information.
8. **Settings** — API/security/execution posture.

## Verification

Acceptance tests are in `tests/unit/test_phase66_web_control.py`. They verify same-origin UI delivery, API reuse, security headers, localhost-only binding, and static traversal protection. Repository-wide CI additionally verifies build/distribution, wheel installation, repository audit, integration verification, Ruff, compileall, and the complete pytest suite.

## Closure rule

Phase 66 is complete only after the implementation, security/accessibility tests, repository-wide validation, documentation synchronization, and final exact-tree `main` CI are green. No phase-66 completion claim is valid before that final gate.
