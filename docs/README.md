# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–52**. Phases **46, 47, 49, and 50** have additionally passed advanced hardening. **Phase 53 — Persistent Sessions is now in implementation.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative V4 roadmap and `architecture/PHASES.md` for phase status/evidence. The Phase 53 implementation record is `architecture/PHASE_53_PERSISTENT_SESSIONS.md`.

## Phase 52 closure

Phase 52 is fully closed on `main`. Final synchronized-tree mainline CI #1020 (`34673411916`) passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest.

## Phase 53 — Persistent Sessions

Phase 53 implements durable SI Core session IDs/lifecycle/ownership, session history/state, ordered events and replay, artifacts/evidence, token/cost history, isolation, recovery, expiration/archival, export/import, cloning/branching, search/filtering, persistent OpenCode/harness continuity, and cross-interface session continuity.

The implementation uses a SQLite-backed `SessionStore` plus `PersistentSessionAdapter`. It re-checks subject/project/harness authority on every operation, uses optimistic revisions, rejects secret-like state, bounds persisted inputs, and keeps replay read-only.

## V4 product surfaces

Web, TUI, CLI, and OpenCode remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session authority.

## Planned Phases 54–71

The roadmap remains unchanged after Phase 53: Human-in-the-Loop, Durable Waiting + Scheduling, Intelligent Routing + Economics, Security Platform, Workspace/Worktree Lifecycle, Observability, Evaluation + Benchmarking, Continuous Improvement, Cross-Runtime/Cross-Harness, Ecosystem/Marketplace, SDK/Developer Platform, Workflow + Automation, Advanced Web, Advanced TUI, Advanced CLI, npm Distribution + Setup, End-to-End Production Validation, and Final Production Hardening.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
