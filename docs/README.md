# Documentation

## Current baseline

SI-Agents V4 has completed Phases **44–51**. Phase 51 adds durable checkpoints and verified resume boundaries; Phase 52 is next.

## Architecture

- `architecture/SI_AGENTS_V4_PLAN.md` — authoritative V4 roadmap and design gates
- `architecture/PHASES.md` — phase status and integration evidence
- `architecture/PHASE_51_CHECKPOINTS_RESUME.md` — Phase 51 design and acceptance evidence
- Runtime implementation: `core/runtime/checkpoints.py`
- Runtime tests: `tests/test_phase51_checkpoints.py`

## Phase closure rule

After every phase, implementation evidence, security/adversarial coverage, documentation, current/index documents, and CI verification are synchronized. Phase 51 final exact-tree CI run 977 / `34627956634` is green.
