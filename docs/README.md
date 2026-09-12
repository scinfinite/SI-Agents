# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–67**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened. **Phase 67 — Advanced TUI Control Center is complete at 100%; Phase 68 — Advanced CLI Platform is next.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap, `architecture/README.md` for the current architecture summary, and `architecture/PHASES.md` for phase evidence.

## Phase 67 — Advanced TUI Control Center

**100% complete and closed.** Phase 67 provides a dependency-free, keyboard-first terminal operator cockpit over the existing Control API. It preserves the historical 14-view surface while adding bounded selection, filtering, deterministic sorting, detail inspection, pause/live state, direct navigation, bounded JSON status export, non-interactive rendering, governed run creation, and identity-bound approval controls.

The TUI is only a client of SI Core: it owns ephemeral presentation state, never invokes a shell or provider directly, and routes supported mutations through existing governed Control API methods. Page size is bounded to 1–100, unknown commands are inert, and `NO_COLOR` is supported. Acceptance coverage is in `tests/test_phase67_tui.py` with the Phase 41 regression suite retained.

Closure evidence: PR #80 merged successfully. Final PR CI **#1288** / run **34702115990** on commit `51eefc53a9d6a9073874d982a4e5c41be08269e2` completed successfully, with the SDK workflow also green (run **34702115987**). Post-merge documentation synchronization is now being validated by mainline CI.

## Phase 66 — Advanced Web Control Plane

**100% complete and closed.** Phase 66 provides a secure, accessible, same-origin, dependency-free operational web client over the existing WebServer and versioned Control API.

## Phase 65 — Workflow + Automation

**100% complete.** Phase 65 provides a transport-neutral workflow state machine with versioned declarative DAGs, branching, bounded fan-out/loops, delegation, human gates, durable waits, triggers, retries, limits, cancellation, idempotency, checkpoints, templates, restart validation, and compensation.

## Closed-phase evidence

- Phase 61: merged PR #75 / PR CI #1157 (`34692165853`).
- Phase 62: merged PR #76; final mainline CI #1186 (`34693756693`) green.
- Phase 63: merged PR #77; final exact-tree mainline CI #1198 (`34694418960`) green.
- Phase 64: merged PR #78; closure CI #1239 (`34697885027`) passed.
- Phase 65: final synchronized-tree CI #1249 (`34698187600`) completed successfully.
- Phase 66: merged PR #79; final synchronized-tree mainline CI #1284 (`34701494501`) completed successfully.
- Phase 67: merged PR #80; final PR CI #1288 (`34702115990`) completed successfully.

## V4 product surfaces

Web, TUI, CLI, OpenCode, SDKs, workflows, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 68 — Advanced CLI Platform.**

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green. **Phase 67 has passed its implementation/PR gate and is being finalized on main.**
