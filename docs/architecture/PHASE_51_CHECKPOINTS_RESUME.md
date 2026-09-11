# Phase 51 — Checkpoints + Resume

## Final status

**Complete pending the final exact-tree CI gate for this documentation synchronization.**

## Scope

Phase 51 makes long-running executions restartable without treating snapshots as authority. A checkpoint is an immutable progress boundary; resume verifies the boundary and creates a fresh authoritative attempt.

## Implementation

- `core/runtime/checkpoints.py`
  - `CheckpointStore`
  - `Checkpoint`
  - `ResumePlan`
  - `CheckpointError`
- `core/runtime/__init__.py` exports the public contracts.
- `tests/test_phase51_checkpoints.py` covers persistence, lineage, integrity, security, size limits, resume, and authority boundaries.

## Security properties

- Append-only checkpoint persistence.
- Per-execution monotonic sequence and parent lineage.
- SHA-256 digest over identity, lineage, state, metadata, timestamp, and schema version.
- Tampering and broken lineage fail closed.
- Secret-like keys are rejected before persistence.
- Serialized state plus metadata is capped at 256 KiB.
- Resume is denied for active executions.
- Resume creates the next attempt only through `ExecutionStore.new_attempt()`.
- Checkpoint metadata never grants capabilities, credentials, provider authority, or identity.
- Checkpoint resume is an explicit retry boundary; exactly-once execution is not claimed.

## Verification

Phase 50 prerequisite was closed on `main` at `9222379cfcb091858f0c5dcc1ec1616f933fca38`; final Phase 50 docs CI was run `34625819419`.

Phase 51 implementation was merged to `main` after the implementation branch CI gate. The current documentation synchronization is the final exact-tree gate. Closure requires repository audit, distribution/wheel install/import, integration verification, Ruff, compileall, and full pytest to pass after the docs update.
