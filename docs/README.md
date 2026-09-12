# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–56**. Phases **46, 47, 49, and 50** have additionally passed advanced hardening. **Phase 57 — Security Platform is next.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative V4 roadmap and `architecture/PHASES.md` for phase status/evidence. The Phase 56 implementation record is `architecture/PHASE_56_INTELLIGENT_ROUTING_ECONOMICS.md`.

## Phase 56 closure

Phase 56 is fully closed. It provides deterministic SI-side intelligent routing over capability, context, streaming, structured output, vision, coding, reasoning, tool use, quality, reliability, latency, cost, provider/model preference, quota, health, circuit state, budgets, retry economics, fallback, escalation/downgrade, failure classification, and non-secret route evidence while preserving OmniRoute as the model/provider/API routing boundary.

PR #67 merged the implementation. Verification CI #1091 (`34682603137`) passed the repository gates, and final synchronized-tree mainline CI #1095 (`34682748193`) passed distribution, wheel verification, repository audit, integration verification, Ruff, compileall, and full pytest.

## Phase 55 closure

Phase 55 is fully closed. It provides durable SQLite-backed waits, timer/delayed/recurring/cron scheduling, event/resource/human/external wake-up, deadlines and fail-closed expiry, restart-safe recovery, priority plus age-based starvation resistance, explicit `waiting → ready → claimed → completed` lifecycle, optimistic revisions, bounded queue/payload limits, secret-like field rejection, ordered lifecycle events, and Control API routes with subject/project isolation.

Closure evidence: final synchronized-tree CI #1080 (`34678317246`).

The authority boundary is explicit: waiting state and scheduling belong to SI Core; the Control API is a transport surface; a wait claim never grants credentials, capabilities, provider authorization, or execution authority.

## V4 product surfaces

Web, TUI, CLI, and OpenCode remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait authority.

## Planned Phases 57–71

The roadmap continues with Security Platform, Workspace/Worktree Lifecycle, Observability, Evaluation + Benchmarking, Continuous Improvement, Cross-Runtime/Cross-Harness, Ecosystem/Marketplace, SDK/Developer Platform, Workflow + Automation, Advanced Web, Advanced TUI, Advanced CLI, npm Distribution + Setup, End-to-End Production Validation, and Final Production Hardening.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
