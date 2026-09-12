# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–53**. Phases **46, 47, 49, and 50** have additionally passed advanced hardening. **Phase 54 — Human-in-the-Loop is next.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative V4 roadmap and `architecture/PHASES.md` for phase status/evidence. The Phase 53 implementation record is `architecture/PHASE_53_PERSISTENT_SESSIONS.md`.

## Phase 52 closure

Phase 52 is fully closed on `main`. Final exact-tree mainline CI #1020 (`34673411916`) passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest.

## Phase 53 closure

Phase 53 is fully closed on `main`. It provides durable SQLite-backed SI Core sessions with lifecycle/ownership isolation, harness binding, optimistic revisions, durable state/context/token-cost history, ordered events/replay, artifact evidence, expiration/archival, export/import, clone/branch lineage, bounded search, restart recovery, and persistent OpenCode/runtime continuity. Security tests cover ownership isolation, stale writes, secret leakage, schema/ownership validation, expiry/archive, artifact limits, replay, cloning, JSON safety, and harness mismatch.

Closure evidence: implementation merge commit `671458a47dc6a3ce6ff79dfdc5acb4ffdb32fc09`, mainline CI #1021 (`34674234547`), followed by the final documentation-synchronized mainline CI gate.

## V4 product surfaces

Web, TUI, CLI, and OpenCode remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session authority.

## Planned Phases 54–71

The roadmap remains unchanged after Phase 53: Human-in-the-Loop, Durable Waiting + Scheduling, Intelligent Routing + Economics, Security Platform, Workspace/Worktree Lifecycle, Observability, Evaluation + Benchmarking, Continuous Improvement, Cross-Runtime/Cross-Harness, Ecosystem/Marketplace, SDK/Developer Platform, Workflow + Automation, Advanced Web, Advanced TUI, Advanced CLI, npm Distribution + Setup, End-to-End Production Validation, and Final Production Hardening.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
