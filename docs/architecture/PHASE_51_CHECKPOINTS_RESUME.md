# Phase 51 — Checkpoints + Resume

## Status

**Implementation complete; final CI verification pending.**

## Objective

Make long-running V4 executions restartable without treating in-memory state, conversation history, or an agent claim as authoritative. Checkpoints persist a compact, integrity-checked progress snapshot; resume verifies that snapshot and creates a fresh execution attempt from the saved boundary.

## Delivered

- `core/runtime/checkpoints.py` adds `CheckpointStore`, `Checkpoint`, `ResumePlan`, and `CheckpointError`.
- SQLite-backed checkpoints are append-only and durably ordered per execution.
- Every checkpoint has a schema version, immutable identifier, sequence, parent lineage, canonical SHA-256 digest, task/attempt identity, state, and metadata.
- Checkpoint state and metadata reject secret-like fields and enforce a 256 KiB serialized state/metadata ceiling.
- `verify()` recomputes the digest and validates parent lineage; `verify_lineage()` checks contiguous sequence and every checkpoint in the chain.
- `resume()` verifies the selected checkpoint, revalidates execution/task identity, refuses active executions, and creates a new runtime attempt through the authoritative `ExecutionStore`.
- Resume returns a `ResumePlan` containing only the checkpoint progress state and new attempt identity; checkpoint metadata/authority is not silently converted into runtime authority.
- Optional Phase 45 `EventBus` integration emits checkpoint-created and checkpoint-resumed facts.
- Package exports expose the checkpoint contracts through `core.runtime`.

## Security and recovery invariants

1. Checkpoints are immutable append-only records; there is no destructive update/delete API.
2. A checkpoint digest covers identity, lineage, state, metadata, timestamp, and schema version.
3. Resume fails closed on missing/tampered checkpoints or broken lineage.
4. A checkpoint cannot inherit from another execution's lineage.
5. Resume cannot start a competing attempt while the current execution is active.
6. Resume reuses the existing authoritative runtime identity and calls `ExecutionStore.new_attempt()`; it never fabricates an attempt ID.
7. Secret-like state/metadata keys are rejected before persistence.
8. Resuming a checkpoint does not restore authorization, credentials, provider grants, or other authority from the snapshot.
9. The persisted checkpoint is a progress boundary, not a claim of exactly-once execution; retried work remains subject to the runtime's idempotency contract.
10. The state-size limit prevents unbounded checkpoint amplification.

## External design references

The design generalizes useful patterns from current ECC checkpoint commands, which treat checkpoints as explicit verification/progress boundaries, and from durable workflow systems that preserve checkpoint lineage and resume from a verified snapshot. SI-Agents deliberately keeps authorization outside checkpoint state and re-enters through the authoritative runtime boundary rather than restoring authority from a snapshot.

## Evidence

`tests/test_phase51_checkpoints.py` covers durable persistence/reopen, ordering and lineage, digest tampering, secret rejection, size limits, cross-execution parent rejection, terminal-only resume, new-attempt creation, active-execution refusal, and authority separation.

## Acceptance

Phase 51 is complete only after the implementation and tests pass the repository's distribution, wheel import, audit, integration, Ruff, compileall, full pytest, and final exact-tree CI gates. The phase record and all current/index documents must be synchronized to the verified result before closure.
