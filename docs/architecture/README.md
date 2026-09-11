# Architecture Index

## Authority order

1. `PHASES.md` — current implementation status and verification evidence.
2. `SI_AGENTS_V4_PLAN.md` — current V4 roadmap and planning direction.
3. `SI_AGENTS_V3.md` — completed V3 architecture and historical contracts.
4. Detailed phase documents — phase-specific contracts and evidence.
5. Cross-cutting contracts — CLI, execution backends, model routing and verification.

Code, executable contracts, governance decisions, and CI results outrank prose when they conflict.

## Current phase index

V3 Phases **1–43 are complete and CI-verified**. V4 Phases **44–49 are complete and final-CI verified**. Phase **50 — Capability Authorization** is next.

| Phase | Canonical record | State |
|---:|---|---|
| 43 | `PHASE_43_INTEGRATION_HARDENING.md` | Complete + CI verified |
| 44 | `PHASE_44_EXECUTION_RUNTIME.md` | Complete + CI verified |
| 45 | `PHASE_45_EVENT_BUS_STATE.md` | Complete + CI verified |
| 46 | `PHASE_46_PARALLEL_SCHEDULER_EXECUTOR.md` | Complete + CI verified |
| 47 | `PHASE_47_OPENCODE_BRIDGE.md` | Complete + CI verified |
| 48 | `PHASE_48_OMNIROUTE_INTEGRATION.md` | Complete + final-CI verified |
| 49 | `PHASE_49_AGENT_TEAM_BUILDER.md` | Complete + final-CI verified |
| 50–71 | `SI_AGENTS_V4_PLAN.md` | Planned |

## Cross-cutting architecture

- One SI Core and one Control API remain the authority boundaries.
- CLI, Web and TUI are control surfaces, not independent authorities.
- Evidence is explicit and provenance-bearing.
- V4 now has a durable runtime, event/state model, dependency-aware scheduler, OpenCode bridge, OmniRoute model/provider adapter, and deterministic agent/team composition layer.
- OpenCode remains the interactive coding harness; OmniRoute remains downstream model/provider routing infrastructure.
- Model selection and agent/team composition cannot grant authority or capabilities.
- Credentials are references and must not become runtime state.
- Web is the richest planned V4 control plane; TUI is the fastest operator surface; CLI is the strongest automation surface.

## Documentation maintenance

`PHASES.md` is authoritative for current status. Historical phase records preserve phase-time evidence and are not rewritten merely to reflect later work. Current/index Markdown must be updated whenever implementation status or architecture direction changes.

**Required after every completed phase:** update the phase record, `PHASES.md`, this architecture index, project/documentation navigation, roadmap status, verification references, and affected cross-cutting contracts before the final exact-tree CI gate.