# SI-Agents Documentation

This directory is the maintained documentation surface for SI-Agents. Documentation distinguishes **current truth**, **historical implementation records**, **v4 planning**, and **governance/policy**.

## Start here

1. **Project overview:** `../README.md`
2. **Current phase/status:** `architecture/PHASES.md`
3. **Architecture index:** `architecture/README.md`
4. **V4 plan:** `architecture/SI_AGENTS_V4_PLAN.md`
5. **Completed V3 architecture:** `architecture/SI_AGENTS_V3.md`
6. **Phase 43 record:** `architecture/PHASE_43_INTEGRATION_HARDENING.md`
7. **CLI contract:** `architecture/CLI.md`
8. **Execution backends:** `architecture/EXECUTION_BACKENDS.md`
9. **Development verification:** `architecture/DEVELOPMENT_VERIFICATION.md`
10. **Engineering rules:** `../AGENTS.md`
11. **IP/provenance policy:** `../governance/legal/IP_PROVENANCE.md`

The Phase 29–43 canonical records remain available from the architecture directory and preserve their phase-specific evidence.

## Source-of-truth rules

- `architecture/PHASES.md` is authoritative for current implementation status and verification.
- `architecture/README.md` is the maintained architecture navigation/index.
- `architecture/SI_AGENTS_V4_PLAN.md` is authoritative for the current V4 planning direction and its Phase 44–71 roadmap until implementation changes the contracts.
- Phase records are authoritative for their completed phase-time evidence.
- Runtime code, executable contracts, governance decisions, and CI results outrank prose when they conflict.
- Documentation must never claim a stronger implementation state than available evidence supports.

## Documentation lifecycle

When an implementation contract changes: implement and test; run the relevant verification; update the current status/index documentation; preserve historical evidence; and update the relevant phase record when the change belongs to an active phase.

## Security and provenance

Markdown is documentation/configuration, not an authority boundary. Imported or externally inspired content must not silently grant permissions or execute code. Material design influence must follow the project's provenance policy and be independently implemented.

## Current baseline

**Phases 1–43 are complete and CI-verified. V3 is closed. V4 planning is established through Phase 71; Phase 44 implementation has not started on `main`.**

The final V3 mainline verification was CI #886 (`34558002476`), with distribution, wheel installation, repository audit, Ruff, and the complete pytest suite passing.

The Phase 44 execution-runtime contract has been prepared as a contract-freeze candidate on dedicated planning work. That preparation is architectural input, not implementation evidence and does not change the Phase 44 status on `main`.

## V4 roadmap

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

## Documentation status

Current-status/index Markdown files are living documents and must reflect the latest verified status. Historical phase Markdown is intentionally not rewritten merely to reflect later V4 plans; those files preserve the evidence and contracts that were true when their phases were completed.
