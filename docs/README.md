# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–60** at the required advanced-hardening level. **Phase 61 — Continuous Improvement is implemented on the current Phase 61 branch and is pending final CI/merge closure.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative V4 roadmap, `architecture/README.md` for the current architecture summary, `architecture/PHASES.md` for phase status/evidence, and `architecture/PHASE_61_CONTINUOUS_IMPROVEMENT.md` for the Phase 61 contract.

## Recent V4 closure records

- **Phase 57 — Security Platform:** complete; final synchronized-tree mainline CI #1113 (`34684260315`).
- **Phase 58 — Workspace / Worktree Lifecycle:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- **Phase 59 — Observability:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- **Phase 60 — Evaluation + Benchmarking:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).

## Phase 61 — Continuous Improvement

The new authority converts evaluation evidence into bounded failure clusters, regression signals, explainable optimization recommendations, deterministic experiments, fail-closed canary decisions, human approval requirements for consequential changes, rollback plans, and tamper-evident improvement history.

It deliberately does **not** mutate agents, teams, models, routing, or workflows directly. Existing SI Core execution, security, deployment/workspace, and governance authorities remain responsible for any approved change.

## V4 product surfaces

Web, TUI, CLI, and OpenCode remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Planned follow-on phases

Phase 62 Cross-Runtime/Cross-Harness, Phase 63 Ecosystem/Marketplace, Phase 64 SDK/Developer Platform, Phase 65 Workflow + Automation, Phase 66 Advanced Web Control Plane, Phase 67 Advanced TUI Control Center, Phase 68 Advanced CLI Platform, Phase 69 npm Distribution + Setup, Phase 70 End-to-End Production Validation, and Phase 71 Final Production Hardening.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
