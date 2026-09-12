# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–65**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened. **Phase 66 — Advanced Web Control Plane is next.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap, `architecture/README.md` for the current architecture summary, `architecture/PHASES.md` for phase evidence, and `architecture/PHASE_65_WORKFLOW_AUTOMATION.md` for the workflow contract.

## Phase 65 — Workflow + Automation

**100% complete.** Phase 65 provides a transport-neutral workflow state machine with versioned declarative DAGs, conditional branching, bounded fan-out and loops, delegation, human approval gates, durable waits, event/webhook/interval triggers, retries, runtime limits, cancellation, request-fingerprint-bound idempotency, durable JSON checkpoints, templates/import/export, restart validation, and reverse-order compensation.

SI Core remains the authority for authorization, execution, evidence, lifecycle, persistence, recovery, and governance. Workflow adapters never create competing authority.

Implementation: `core/automation/workflows.py`.

Verification: `tests/unit/test_phase65_workflows.py` and repository-wide CI. Final synchronized-tree CI #1249 (`34698187600`) passed distribution build, wheel verification, repository audit, integration verification, Ruff, and full pytest.

## Phase 64 — SDK / Developer Platform

Phase 64 provides typed Python and TypeScript SDKs, versioned REST/SSE/WebSocket access, stable errors, optional bearer authentication, header-bound identity, cursor pagination/filtering, idempotent run creation, bounded concurrency, explicit SSE/webhook subscription lifecycle, signed webhook delivery primitives, OpenAPI updates, package metadata, examples, and dedicated SDK CI.

SDKs remain clients/adapters. SI Core remains authoritative for authorization, execution, evidence, lifecycle, persistence, and governance.

## Closed-phase evidence

- Phase 61: merged PR #75 / PR CI #1157 (`34692165853`).
- Phase 62: merged PR #76; final mainline CI #1186 (`34693756693`) green.
- Phase 63: merged PR #77; final exact-tree mainline CI #1198 (`34694418960`) green.
- Phase 64: merged PR #78; implementation-tree CI #1239 (`34697885027`) passed the repository closure suite.
- Phase 65: final synchronized-tree CI #1249 (`34698187600`) completed successfully.

## V4 product surfaces

Web, TUI, CLI, OpenCode, SDKs, workflows, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 66 — Advanced Web Control Plane.**

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green. **Phase 65 satisfies this gate.**
