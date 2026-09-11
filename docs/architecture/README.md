# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, runtime adapters, schedulers, agents, and integrations are clients of that authority rather than independent state owners.

## Verified V4 phases

| Phase | Capability | Status |
|---:|---|---|
| 44 | Execution Runtime Foundation | Complete |
| 45 | Event Bus + State Architecture | Complete |
| 46 | Parallel Scheduler + Executor | Complete |
| 47 | OpenCode Bridge | Complete |
| 48 | OmniRoute Integration | Complete |
| 49 | Agent + Team Builder | Complete |
| 50 | Capability Authorization | Complete |
| 51 | Checkpoints + Resume | Complete pending final docs-tree CI |

## Phase 51 authority rules

Checkpoints are progress evidence, not authority. Their snapshots cannot restore credentials, capabilities, grants, provider authorization, or identity. Resume is performed through `ExecutionStore.new_attempt()` after checkpoint integrity, lineage, execution identity, and terminal-state checks.

## Next

Phase 52 — Context / Memory Economics.

See `SI_AGENTS_V4_PLAN.md` and `PHASES.md` for the complete roadmap and closure evidence.
