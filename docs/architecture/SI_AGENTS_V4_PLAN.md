# SI-Agents V4 Plan

## Current verified position

V3 is closed. V4 implementation has completed Phases 44–51 in sequence. Phase 50 was fully closed on `main` at `9222379cfcb091858f0c5dcc1ec1616f933fca38`, with final documentation CI run `34625819419`. Phase 51 implementation is merged to `main`; final exact-tree CI run 977 / `34627956634` is green.

## Architecture direction

The V4 target is a governed execution platform with one authoritative SI Core. Web, TUI, CLI, agent teams, workflow automation, and external harnesses integrate through explicit runtime and governance boundaries.

Core principles:

1. Durable state is authoritative; UI state is not.
2. Authorization is explicit and fail-closed.
3. Checkpoints preserve progress, never authority.
4. Retries/resume create explicit attempts and preserve provenance.
5. External providers are adapters, never authority owners.
6. Evidence and verification are required before phase closure.
7. Current/index documentation is synchronized after every phase.

## Phase roadmap

44 — Execution Runtime Foundation  
45 — Event Bus + State Architecture  
46 — Parallel Scheduler + Executor  
47 — OpenCode Bridge  
48 — OmniRoute Integration  
49 — Agent + Team Builder  
50 — Capability Authorization  
51 — Checkpoints + Resume  
52 — Context / Memory Economics  
53 — Persistent Sessions  
54 — Human-in-the-Loop  
55 — Durable Waiting + Scheduling  
56 — Intelligent Routing + Economics  
57 — Security Platform  
58 — Workspace / Worktree Lifecycle  
59 — Observability  
60 — Evaluation + Benchmarking  
61 — Continuous Improvement  
62 — Cross-Runtime / Cross-Harness  
63 — Ecosystem / Marketplace  
64 — SDK / Developer Platform  
65 — Workflow + Automation  
66 — Advanced Web Control Plane  
67 — Advanced TUI Control Center  
68 — Advanced CLI Platform  
69 — npm Distribution + Setup  
70 — End-to-End Production Validation  
71 — Final Production Hardening

## Phase 51 summary

Phase 51 introduces `CheckpointStore`, `Checkpoint`, `ResumePlan`, and `CheckpointError` in `core/runtime/checkpoints.py`.

- SQLite append-only persistence with ordered per-execution lineage.
- SHA-256 canonical integrity digests.
- Parent checkpoint validation and lineage verification.
- Secret-like field rejection and 256 KiB serialized state/metadata limit.
- Durable reopen behavior.
- Terminal-only resume through authoritative `ExecutionStore.new_attempt()`.
- Resume plans preserve checkpoint progress while deliberately excluding metadata-derived authority.
- Optional EventBus facts for checkpoint creation/resume.
- Tests cover tampering, lineage, secrets, size, active-execution rejection, terminal resume, and persistence.

## Closure gate

Every phase requires implementation, tests, security/adversarial checks, documentation, all current/index document updates, and final CI verification. Final CI must cover repository audit, distribution/wheel install/import, integration verification, Ruff, compileall, and full pytest. Phase 51 final exact-tree CI run 977 / `34627956634` is green.
