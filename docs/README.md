# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–61**. Phases **58–60** are closed at the required advanced-hardening level, and **Phase 61 — Continuous Improvement** is fully closed after merged PR #75 and green PR CI #1157 (`34692165853`).

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative V4 roadmap, `architecture/README.md` for the current architecture summary, `architecture/PHASES.md` for phase status/evidence, and `architecture/PHASE_61_CONTINUOUS_IMPROVEMENT.md` for the Phase 61 contract.

## Recent V4 closure records

- **Phase 57 — Security Platform:** complete; final synchronized-tree mainline CI #1113 (`34684260315`).
- **Phase 58 — Workspace / Worktree Lifecycle:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- **Phase 59 — Observability:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- **Phase 60 — Evaluation + Benchmarking:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- **Phase 61 — Continuous Improvement:** complete; PR #75 / CI #1157 (`34692165853`).

## Phase 61 — Continuous Improvement

The authority converts evaluation evidence into bounded failure clusters, regression signals, explainable optimization recommendations, deterministic experiments, fail-closed canary decisions, human approval requirements for consequential changes, rollback plans, and tamper-evident improvement history.

It deliberately does **not** mutate agents, teams, models, routing, or workflows directly. Existing SI Core execution, security, deployment/workspace, and governance authorities remain responsible for any approved change.

## V4 product surfaces

Web, TUI, CLI, and OpenCode remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 62 — Cross-Runtime / Cross-Harness** is next.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
