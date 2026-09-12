# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, runtime adapters, schedulers, agents, and integrations are clients of that authority rather than independent state owners.

## Verified V4 phases

| Phase | Capability | Status |
|---:|---|---|
| 44 | Execution Runtime Foundation | Complete |
| 45 | Event Bus + State Architecture | Complete |
| 46 | Parallel Scheduler + Executor | **Advanced hardened** |
| 47 | OpenCode Bridge | **Advanced hardened** |
| 48 | OmniRoute Integration | Complete |
| 49 | Agent + Team Builder | **Advanced hardened** |
| 50 | Capability Authorization | **Advanced hardened** |
| 51 | Checkpoints + Resume | Complete | CI #977 / `34627956634` |

## Advanced hardening gate

Combined audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite.

Phase 46 now enforces scheduler idempotency and DAG safety. Phase 47 enforces request timeouts and bounded SSE frames. Phase 49 enforces schema-versioned deterministic team topology and execution layers. Phase 50 enforces request-bound approvals and secret-like metadata rejection.

## Phase 51 authority rules

Checkpoints are progress evidence, not authority. Their snapshots cannot restore credentials, capabilities, grants, provider authorization, or identity. Resume is performed through `ExecutionStore.new_attempt()` after checkpoint integrity, lineage, execution identity, and terminal-state checks.

## Next

Phase 52 — Context / Memory Economics.

See `SI_AGENTS_V4_PLAN.md` and `PHASES.md` for the complete roadmap and closure evidence.
