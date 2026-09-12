# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–62**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened, and **Phase 62 — Cross-Runtime / Cross-Harness** is now implemented pending final CI closure.

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap, `architecture/README.md` for the current architecture summary, `architecture/PHASES.md` for phase evidence, and `architecture/PHASE_62_CROSS_RUNTIME_CROSS_HARNESS.md` for the Phase 62 contract.

## Phase 62 — Cross-Runtime / Cross-Harness

Phase 62 provides common portable adapter contracts for runtime, session, tool, model, event, capability, context, checkpoint, and artifact resource families. `CrossRuntimeGateway` provides deterministic harness discovery, capability filtering, health probing, bounded quarantine/recovery, preferred selection, project+harness session binding, explicit migration, and safe pre-start fallback.

Fallback is fail-closed after execution-start signals. Routing evidence excludes request payloads. Registration/discovery never grants execution permission. OpenCode remains a supported harness rather than defining the runtime protocol.

## Previous closure records

- Phase 58–60: advanced-hardening PR #74; PR CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- Phase 61: merged PR #75; PR CI #1157 (`34692165853`).

## V4 product surfaces

Web, TUI, CLI, OpenCode, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 63 — Ecosystem / Marketplace** is next after Phase 62 closure.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
