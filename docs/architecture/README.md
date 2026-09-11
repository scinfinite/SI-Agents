# SI-Agents Architecture Documentation

## Authority order

1. `PHASES.md` — current implementation status and verification evidence.
2. `SI_AGENTS_V4_PLAN.md` — current V4 planning direction and planned Phases 44–71.
3. `SI_AGENTS_V3.md` — completed V3 architecture and historical post-V3 direction.
4. Detailed phase documents — historical contracts and phase evidence.
5. Cross-cutting contracts such as `EXECUTION_BACKENDS.md` and `CLI.md`.

Code, executable contracts, governance decisions, and CI results outrank prose when they conflict; current documentation must be corrected.

## Phase index

Phases **1–43 are complete and CI-verified**. Phase 44 is the next planned implementation phase and has not started on `main`.

| Phase | Canonical record | State |
|---:|---|---|
| 1–28 | Historical `PHASE_<n>_*.md` records | Complete |
| 29 | `PHASE_29_AGENT_PERSONA.md` | Complete + CI verified |
| 30 | `PHASE_30_PORTABLE_SKILLS.md` | Complete + CI verified |
| 31 | `PHASE_31_RULES_HOOKS_EVENTS.md` | Complete + CI verified |
| 32 | `PHASE_32_MEMORY_KNOWLEDGE.md` | Complete + CI verified |
| 33 | `PHASE_33_SECURITY_GOVERNANCE_CENTER.md` | Complete + CI verified |
| 34 | `PHASE_34_ORGANIZATION_EXPANSION.md` | Complete + CI verified |
| 35 | `PHASE_35_CONTROL_API.md` | Complete + CI verified |
| 36 | `PHASE_36_LOCAL_WEB_FOUNDATION.md` | Complete + CI verified |
| 37 | `PHASE_37_CONTROL_CENTER.md` | Complete + CI verified |
| 38 | `PHASE_38_VISUAL_ORGANIZATION_WORKFLOW.md` | Complete + CI verified |
| 39 | `PHASE_39_AGENT_BUILDER.md` | Complete + CI verified |
| 40 | `PHASE_40_EVIDENCE_OBSERVABILITY.md` | Complete + CI verified |
| 41 | `PHASE_41_TUI.md` | Complete + CI verified |
| 42 | `PHASE_42_HARNESS_DEPLOYMENT_CENTER.md` | Complete + CI verified |
| 43 | `PHASE_43_INTEGRATION_HARDENING.md` | Complete + CI verified |
| 44 | `SI_AGENTS_V4_PLAN.md` | Planned / next |
| 45–71 | `SI_AGENTS_V4_PLAN.md` | Planned |

## Cross-cutting architecture

- One SI Core and one Control API remain the authority boundaries.
- CLI, Web, and TUI are control surfaces, not independent authorities.
- Evidence is explicit and provenance-bearing.
- V4 introduces a persistent execution runtime, event/state model, scheduler, sessions and live orchestration while preserving V3 governance boundaries.
- OpenCode remains the interactive coding harness; OmniRoute remains the model/provider routing layer.
- Web is the richest planned V4 control plane; TUI is the fastest operator surface; CLI is the strongest automation surface.
- Surface parity means operationally important capabilities share the same authoritative state and Control API across Web/TUI/CLI.
- ECC and Agency Agents are external engineering references, not copied implementations or authority sources.

## V4 sequence

```text
44 Runtime Foundation
 → 45 Event + State
 → 46 Scheduler / Executor
 → 47 OpenCode Bridge
 → 48 OmniRoute
 → 49 Agent + Team Builder
 → 50 Capability Authorization
 → 51 Checkpoints + Resume
 → 52 Context / Memory Economics
 → 53 Persistent Sessions
 → 54 Human-in-the-Loop
 → 55 Durable Waiting + Scheduling
 → 56 Intelligent Routing + Economics
 → 57 Security Platform
 → 58 Workspace / Worktree Lifecycle
 → 59 Observability
 → 60 Evaluation + Benchmarking
 → 61 Continuous Improvement
 → 62 Cross-Runtime / Cross-Harness
 → 63 Ecosystem / Marketplace
 → 64 SDK / Developer Platform
 → 65 Workflow + Automation
 → 66 Advanced Web Control Plane
 → 67 Advanced TUI Control Center
 → 68 Advanced CLI Platform
 → 69 npm Distribution + Setup
 → 70 End-to-End Production Validation
 → 71 Final Production Hardening
```

## Documentation maintenance

`PHASES.md` is authoritative for current status. `SI_AGENTS_V4_PLAN.md` is the current V4 planning baseline. Historical phase records preserve their phase-time evidence and must not be rewritten merely to reflect later work. Current/index Markdown must be updated whenever implementation status or architecture direction changes.
