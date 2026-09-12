# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–66**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened. **Phase 66 — Advanced Web Control Plane is complete at 100%; Phase 67 — Advanced TUI Control Center is next.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap, `architecture/README.md` for the current architecture summary, and `architecture/PHASES.md` for phase evidence.

## Phase 66 — Advanced Web Control Plane

**100% complete and closed.** Phase 66 provides a secure, accessible, same-origin, dependency-free operational web client over the existing WebServer and versioned Control API. The surface covers dashboard/health, bounded live activity, workflow/run inspection, accessible topology/DAG views, evidence, identity-bound approvals, governed run-request controls, resources/settings, and bounded repository source/search/diff inspection.

The browser remains a client of SI Core and never becomes a second state or authorization authority. Authentication, audit, governance, SSE/WebSocket, and Control API boundaries are inherited from the existing platform. Static and repository inspection paths are traversal-safe and bounded; CSP, `nosniff`, keyboard navigation, semantic landmarks, status announcements, and non-color-only status labels provide the security/accessibility baseline.

Implementation: `core/web/advanced.py`, `web/control/index.html`, `web/control/app.js`, and `web/control/styles.css`.

Acceptance tests: `tests/unit/test_phase66_web_control.py` and `tests/unit/test_phase66_advanced_web.py`.

Closure evidence: PR #79 merged successfully. Final synchronized-tree mainline CI **#1280** / run **34699748468** on commit `89e59f31c5785ab7a29aab8eec927cbebaa3b383` completed successfully; the CI workflow concluded `success`, and the SDK workflow on the same commit also concluded `success` (run **34699748479**). This is the authoritative final closure evidence for the synchronized documentation state.

## Phase 65 — Workflow + Automation

**100% complete.** Phase 65 provides a transport-neutral workflow state machine with versioned declarative DAGs, conditional branching, bounded fan-out and loops, delegation, human approval gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates/import/export, restart validation, and reverse-order compensation.

SI Core remains the authority for authorization, execution, evidence, lifecycle, persistence, recovery, waiting, workspace, and governance.

Verification: final synchronized-tree CI #1249 (`34698187600`) passed distribution build, wheel verification, repository audit, integration verification, Ruff, and full pytest.

## Closed-phase evidence

- Phase 61: merged PR #75 / PR CI #1157 (`34692165853`).
- Phase 62: merged PR #76; final mainline CI #1186 (`34693756693`) green.
- Phase 63: merged PR #77; final exact-tree mainline CI #1198 (`34694418960`) green.
- Phase 64: merged PR #78; implementation-tree CI #1239 (`34697885027`) passed the repository closure suite.
- Phase 65: final synchronized-tree CI #1249 (`34698187600`) completed successfully.
- Phase 66: merged PR #79; final synchronized-tree mainline CI #1280 (`34699748468`) completed successfully.

## V4 product surfaces

Web, TUI, CLI, OpenCode, SDKs, workflows, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 67 — Advanced TUI Control Center.**

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green. **Phase 66 satisfies this gate.**
