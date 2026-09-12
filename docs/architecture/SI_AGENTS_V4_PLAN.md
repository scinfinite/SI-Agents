# SI-Agents V4 Plan

## Current verified position

V3 is closed. V4 implementation has completed Phases 44–51 in sequence. Phase 51 is complete. A subsequent advanced-level audit of Phases 46, 47, 49, and 50 identified and closed production-hardening gaps without reopening the phase sequence.

## Advanced hardening position

Combined advanced audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite.

### Phase 46 — Parallel Scheduler + Executor

- Explicit execution identity reuse is checked at the scheduler boundary.
- Idempotent submissions return the existing schedule only when orchestration metadata matches.
- Conflicting resubmissions cannot mutate existing schedules or surface raw runtime uniqueness errors.
- Dependency graph cycle defense is explicit.
- Existing durable recovery, bounded concurrency, cancellation propagation, and event integration remain intact.

### Phase 47 — OpenCode Bridge

- Per-request timeout budgets propagate to HTTP/SSE transport.
- SSE frame buffering is capped at 1 MiB.
- Streaming requires explicit terminal events.
- Existing loopback-default, session filtering, cancellation, error normalization, and authority boundaries remain intact.

### Phase 49 — Agent + Team Builder

- Agent/team catalogs and manifests are schema-versioned.
- Definition validation rejects duplicate metadata and invalid declarations.
- Handoff graphs are acyclic.
- Deterministic topological execution layers expose parallel composition opportunities without granting authority.

### Phase 50 — Capability Authorization

- High/critical approvals are bound to the exact request fingerprint.
- Approval replay against modified authorization inputs is rejected.
- Secret-like metadata keys are rejected before evidence creation.
- Governance input sizes are bounded and egress semantics remain explicit/fail-closed.

## Architecture direction

The V4 target is a governed execution platform with one authoritative SI Core. Web, TUI, CLI, agent teams, workflow automation, and external harnesses integrate through explicit runtime and governance boundaries.

Core principles:

1. Durable state is authoritative; UI state is not.
2. Authorization is explicit and fail-closed.
3. Checkpoints preserve progress, never authority.
4. Retries/resume create explicit attempts and preserve provenance.
5. External providers are adapters, never authority owners.
6. Evidence and verification are required before phase closure.
7. Current/index documentation is synchronized after every phase and hardening audit.

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

Every phase and hardening audit requires implementation, security/adversarial tests, documentation synchronization, all current/index document updates, and final CI verification. Final CI must cover repository audit, distribution/wheel install/import, integration verification, Ruff, compileall, and full pytest. The advanced hardening implementation gate is CI #984; the documentation-synchronized tree must pass its own final exact-tree CI before these changes are merged to `main`.
