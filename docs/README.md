# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–60** at the required advanced-hardening level. Phases **46, 47, 49, and 50** were previously advanced-hardened; Phases **58, 59, and 60** have now also passed a dedicated advanced-hardening audit and final mainline CI. **Phase 61 — Continuous Improvement is next.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative V4 roadmap, `architecture/README.md` for the current architecture summary, and `architecture/PHASES.md` for phase status/evidence.

## Recent V4 closure records

- **Phase 57 — Security Platform:** complete; final synchronized-tree mainline CI #1113 (`34684260315`).
- **Phase 58 — Workspace / Worktree Lifecycle:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- **Phase 59 — Observability:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).
- **Phase 60 — Evaluation + Benchmarking:** advanced hardened; PR #74 / CI #1143 (`34691131729`), final mainline CI #1144 (`34691176676`).

## Advanced-hardening outcomes

- **Phase 58:** adversarial event-chain tamper detection and sensitive-operation authorization callback coverage were added to the existing isolation, lock, revision, filesystem, Git, cleanup, and recovery contracts.
- **Phase 59:** shared security-scanner credential detection, stricter resource bounds, and complete bounded integrity scanning were added; tampering beyond the first query page is now covered by tests.
- **Phase 60:** documented cost/latency budgets are now enforceable release gates; secret-bearing evaluator outputs, metadata, and review rationale are rejected; persisted evidence can be integrity-verified; experiment inputs are tightened; empty reporting fails closed.

## Phase 56 closure

Phase 56 is fully closed. It provides deterministic SI-side intelligent routing over capability, context, streaming, structured output, vision, coding, reasoning, tool use, quality, reliability, latency, cost, provider/model preference, quota, health, circuit state, budgets, retry economics, fallback, escalation/downgrade, failure classification, and non-secret route evidence while preserving OmniRoute as the model/provider/API routing boundary.

PR #67 merged the implementation. Verification CI #1091 (`34682603137`) passed the repository gates, and the final synchronized-tree mainline evidence is recorded in the Phase 56 architecture document.

## Phase 55 closure

Phase 55 is fully closed. It provides durable SQLite-backed waits, timer/delayed/recurring/cron scheduling, event/resource/human/external wake-up, deadlines and fail-closed expiry, restart-safe recovery, priority plus age-based starvation resistance, explicit `waiting → ready → claimed → completed` lifecycle, optimistic revisions, bounded queue/payload limits, secret-like field rejection, ordered lifecycle events, and Control API routes with subject/project isolation.

Closure evidence: final synchronized-tree CI #1080 (`34678317246`).

The authority boundary is explicit: waiting state and scheduling belong to SI Core; the Control API is a transport surface; a wait claim never grants credentials, capabilities, provider authorization, or execution authority.

## V4 product surfaces

Web, TUI, CLI, and OpenCode remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait authority.

## Planned Phases 61–71

The next roadmap phase is **Phase 61 — Continuous Improvement**. Planned follow-on phases are Cross-Runtime/Cross-Harness, Ecosystem/Marketplace, SDK/Developer Platform, Workflow + Automation, Advanced Web Control Plane, Advanced TUI Control Center, Advanced CLI Platform, npm Distribution + Setup, End-to-End Production Validation, and Final Production Hardening.

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
