# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents.

## Primary navigation

1. `../README.md` — project overview and current status.
2. `architecture/README.md` — architecture index.
3. `architecture/PHASES.md` — authoritative current implementation status.
4. `architecture/SI_AGENTS_V4_PLAN.md` — V4 roadmap and acceptance gates.
5. `architecture/SI_AGENTS_V3.md` — completed V3 architecture.
6. `architecture/MODEL_ROUTING.md` — model/provider routing contract.
7. `architecture/PHASE_44_EXECUTION_RUNTIME.md` — Phase 44 evidence.
8. `architecture/PHASE_45_EVENT_BUS_STATE.md` — Phase 45 evidence.
9. `architecture/PHASE_46_PARALLEL_SCHEDULER_EXECUTOR.md` — Phase 46 evidence.
10. `architecture/PHASE_47_OPENCODE_BRIDGE.md` — Phase 47 evidence.
11. `architecture/PHASE_48_OMNIROUTE_INTEGRATION.md` — Phase 48 evidence.
12. `architecture/CLI.md` — CLI contract.
13. `architecture/EXECUTION_BACKENDS.md` — execution backend contract.
14. `architecture/DEVELOPMENT_VERIFICATION.md` — verification workflow.
15. `../AGENTS.md` — engineering rules.
16. `../governance/legal/IP_PROVENANCE.md` — IP/provenance policy.

## Source-of-truth rules

- `architecture/PHASES.md` is authoritative for current implementation status and verification.
- `architecture/README.md` is maintained architecture navigation.
- `architecture/SI_AGENTS_V4_PLAN.md` is the current V4 roadmap and planning baseline.
- Phase records preserve phase-time evidence.
- Runtime code, executable contracts, governance decisions, and CI results outrank prose when they conflict.
- Documentation must never claim a stronger implementation state than available evidence supports.

## Documentation lifecycle

After every completed phase: implement and test; run relevant verification; update the phase record; update `PHASES.md`; update architecture/project navigation; update the V4 roadmap status; refresh verification references and affected cross-cutting contracts; preserve historical evidence; then run the final exact-tree CI gate.

## Current baseline

**V3 Phases 1–43 are complete and CI-verified. V4 Phases 44–47 are complete and final-CI verified. Phase 48 — OmniRoute Integration — is implementation-complete and awaiting its final CI gate.**

## V4 sequence

```text
44 Runtime → 45 Events/State → 46 Scheduler → 47 OpenCode →
48 OmniRoute → 49 Agents/Teams → 50 Authorization → 51 Resume →
52 Context Economics → 53 Sessions → 54 HITL → 55 Durable Waiting →
56 Routing Economics → 57 Security → 58 Worktrees → 59 Observability →
60 Evaluation → 61 Continuous Improvement → 62 Cross-Runtime →
63 Ecosystem → 64 SDK → 65 Workflow Automation → 66 Web →
67 TUI → 68 CLI → 69 npm → 70 Production Validation → 71 Hardening
```
