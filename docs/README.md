# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–55**. Phases **46, 47, 49, and 50** have additionally passed advanced hardening. **Phase 56 — Intelligent Routing + Economics is next.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative V4 roadmap and `architecture/PHASES.md` for phase status/evidence. The Phase 55 implementation record is `architecture/PHASE_55_DURABLE_WAITING_SCHEDULING.md`.

## Phase 54 closure

Phase 54 is fully closed on `main`. It provides durable human approval/input/review gates, risk and deployment decisions, identity binding, expiry, fail-closed behavior, audit/evidence, and shared Control API semantics without granting execution authority.

Closure evidence: final synchronized-tree mainline CI #1051 (`34676632475`) passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest.

## Phase 55 closure

Phase 55 is implemented and verified. It provides durable SQLite-backed waits, timer/delayed/recurring/cron scheduling, event/resource/human/external wake-up, deadlines and fail-closed expiry, restart-safe recovery, priority plus age-based starvation resistance, explicit `waiting → ready → claimed → completed` lifecycle, optimistic revisions, bounded queue/payload limits, secret-like field rejection, ordered lifecycle events, and Control API routes with subject/project isolation.

Implementation CI #1074 (`34678184341`) passed distribution, wheel verification, repository audit, integration verification, Ruff, and full pytest. The final synchronized-tree mainline CI is the closure gate after this documentation synchronization.

The authority boundary is explicit: waiting state and scheduling belong to SI Core; the Control API is a transport surface; a wait claim never grants credentials, capabilities, provider authorization, or execution authority.

## V4 product surfaces

Web, TUI, CLI, and OpenCode remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait authority.

## Planned Phases 56–71

The roadmap continues with Intelligent Routing + Economics, Security Platform, Workspace/Worktree Lifecycle, Observability, Evaluation + Benchmarking, Continuous Improvement, Cross-Runtime/Cross-Harness, Ecosystem/Marketplace, SDK/Developer Platform, Workflow + Automation, Advanced Web, Advanced TUI, Advanced CLI, npm Distribution + Setup, End-to-End Production Validation, and Final Production Hardening.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
