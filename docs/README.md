# Documentation

## Current baseline

SI-Agents V4 has completed Phases **44–51**. Phases **46, 47, 49, and 50** have now also passed an advanced-level hardening audit. Phase 52 is next.

## Advanced audit evidence

Combined advanced CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite.

- `architecture/PHASE_46_PARALLEL_SCHEDULER_EXECUTOR.md` — scheduler idempotency, DAG safety, recovery and concurrency hardening
- `architecture/PHASE_47_OPENCODE_BRIDGE.md` — timeout propagation and bounded SSE transport hardening
- `architecture/PHASE_49_AGENT_TEAM_BUILDER.md` — schema, topology and deterministic execution planning hardening
- `architecture/PHASE_50_CAPABILITY_AUTHORIZATION.md` — approval binding and governance metadata hardening

## Architecture

- `architecture/SI_AGENTS_V4_PLAN.md` — authoritative V4 roadmap and design gates
- `architecture/PHASES.md` — phase status and integration evidence
- `architecture/PHASE_51_CHECKPOINTS_RESUME.md` — Phase 51 design and acceptance evidence

## Phase closure rule

After every phase and every cross-phase hardening audit, implementation evidence, security/adversarial coverage, documentation, current/index documents, and CI verification are synchronized. The final exact-tree CI gate is required before hardening changes are considered permanently closed on `main`.
