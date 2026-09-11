# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents. Documentation distinguishes **current truth**, **historical implementation records**, **v4 planning**, and **governance/policy**.

## Start here

1. **Project overview:** `../README.md`
2. **Current phase/status:** `architecture/PHASES.md`
3. **Architecture index:** `architecture/README.md`
4. **V4 plan:** `architecture/SI_AGENTS_V4_PLAN.md`
5. **Completed V3 architecture:** `architecture/SI_AGENTS_V3.md`
6. **Phase 44 record:** `architecture/PHASE_44_EXECUTION_RUNTIME.md`
7. **Phase 45 record:** `architecture/PHASE_45_EVENT_BUS_STATE.md`
8. **Phase 46 record:** `architecture/PHASE_46_PARALLEL_SCHEDULER_EXECUTOR.md`
9. **Phase 47 record:** `architecture/PHASE_47_OPENCODE_BRIDGE.md`
10. **CLI contract:** `architecture/CLI.md`
11. **Execution backends:** `architecture/EXECUTION_BACKENDS.md`
12. **Development verification:** `architecture/DEVELOPMENT_VERIFICATION.md`
13. **Engineering rules:** `../AGENTS.md`
14. **IP/provenance policy:** `../governance/legal/IP_PROVENANCE.md`

The Phase 29–43 canonical records remain available from the architecture directory and preserve their phase-specific evidence.

## Source-of-truth rules

- `architecture/PHASES.md` is authoritative for current implementation status and verification.
- `architecture/README.md` is the maintained architecture navigation/index.
- `architecture/SI_AGENTS_V4_PLAN.md` is authoritative for the current V4 planning direction and its Phase 44–71 roadmap; completed phase states are evidence-backed and current status is recorded in `PHASES.md`.
- Phase records are authoritative for their completed phase-time evidence.
- Runtime code, executable contracts, governance decisions, and CI results outrank prose when they conflict.
- Documentation must never claim a stronger implementation state than available evidence supports.

## Documentation lifecycle

After every completed phase: implement and test; run the relevant verification; update the phase record; update `PHASES.md`; update the architecture index and project/documentation navigation; update the V4 roadmap status where applicable; refresh verification baselines and cross-cutting references; preserve historical evidence; and only then run the final exact-tree CI gate.

## Security and provenance

Markdown is documentation/configuration, not an authority boundary. Imported or externally inspired content must not silently grant permissions or execute code. Material design influence must follow the project's provenance policy and be independently implemented.

## Current baseline

**Phases 1–43 are complete and CI-verified. V3 is closed. V4 Phases 44–47 are complete and final-CI verified. Phase 48 — OmniRoute Integration — is next.**

V4 verification currently includes Phase 44 CI #919 (`34610448789`), Phase 45 final exact-tree CI #935 (`34612616978`), Phase 46 final CI #938 (`34615157829`), and Phase 47 implementation CI #941 (`34615709124`) followed by final documentation exact-tree CI #942 (`34615862860`).

## V4 roadmap

```text
44 Runtime Foundation       [complete]
 → 45 Event + State         [complete]
 → 46 Scheduler / Executor  [complete]
 → 47 OpenCode Bridge       [complete]
 → 48 OmniRoute             [next]
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

## Documentation status

Current-status/index Markdown files are living documents and must reflect the latest verified status. Historical phase Markdown is intentionally not rewritten merely to reflect later V4 plans; those files preserve the evidence and contracts that were true when their phases were completed.
