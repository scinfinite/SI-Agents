# Phase 28 — Cross-environment & Handoff

**Status: complete and CI-verified.**

## Objective

Phase 28 makes work portable between the supported Termux and GitHub Codespaces environments without turning either environment into a hidden state authority. A handoff is a signed-by-integrity, JSON-portable snapshot of workflow context, task state, results, checkpoints, and evidence references.

## Contract

The versioned envelope is `si.handoff.v1` and contains:

- source and target environment
- stable project identity when a Git origin is available
- team and workflow execution identity
- optional harness session identity
- objective
- task statuses and attempt counts
- JSON-compatible workflow context
- summarized agent results and evidence IDs
- checkpoints
- creation timestamp
- SHA-256 integrity digest

The envelope deliberately contains no API keys, passwords, authorization headers, provider credentials, or secret-like fields. Secret-like keys are rejected recursively at creation and validation time.

## Commands

```text
si handoff create TEAM --objective TEXT --source termux|codespace --target termux|codespace --output FILE
si handoff inspect FILE
si handoff import FILE
si run TEAM --objective TEXT --handoff FILE
```

`create` executes the existing governed team and exports its portable state. It may export a failed execution as diagnostic state, but returns the same non-success exit code as the team execution. `inspect` verifies the integrity digest before displaying the envelope. `import` verifies integrity, source/target compatibility, and target workspace identity. `run --handoff` resumes from validated context while still executing the canonical team through `TeamEngine` and its existing governance.

## Project identity

When a Git `origin` exists, the handoff records a sanitized repository URL rather than a commit SHA. Embedded HTTP credentials are removed, and SSH identities are canonicalized, allowing a repository to advance commits between environments while still detecting an unrelated repository. If no origin exists, the current Git HEAD is used as a conservative fallback.

Project validation is fail-closed only when both the handoff and target workspace provide identities and they differ. A missing identity does not invent one and does not block otherwise valid portability.

## Storage and integrity

The default local handoff directory is `~/.config/si-agents/handoffs`. Directory permissions are `0700`; individual handoffs are written atomically with `0600` permissions. Export accepts an explicit path so users can transfer the resulting JSON file using GitHub artifacts, a shared filesystem, `scp`, or another operator-controlled mechanism without SI-Agents silently transmitting state.

The handoff digest is computed over a canonical JSON representation and stored alongside the payload. Import/inspect recomputes it and rejects tampering. Sequence fields are normalized during import so JSON arrays round-trip into the typed tuple contract.

## Governance boundary

Handoff state is data, not authority. Import does not:

- enable a harness
- grant permissions
- execute a command
- install software
- copy credentials
- create accounts
- change provider routing
- bypass approvals or Phase 13 governance

The target environment remains authoritative for its own readiness, permissions, credentials, workspace, and harness session. A transferred OpenCode session ID is context only; it is never treated as proof of authorization or as a substitute for a live target session.

## Failure and conflict behavior

- Unsupported handoff schemas are rejected.
- Missing or malformed integrity digests are rejected.
- Secret-like context is rejected rather than redacted silently.
- Same-environment handoffs are rejected.
- Target-environment mismatches are rejected.
- Repository identity mismatches are rejected.
- Handoff files are never executed as code.
- Partial/failed workflow state can be inspected, but successful continuation remains subject to the target team's normal gates.

## Verification evidence

Final mainline CI run **#526** passed all gates on commit `4ccfcfe29693d2a0f76810c000607822938253f4`:

- distribution build and isolated wheel installation
- installed `si` catalog smoke tests
- Ruff
- full pytest suite: **341 passed**
- handoff serialization and atomic storage
- SHA-256 tamper detection
- recursive secret-like field rejection
- Termux/Codespaces target validation
- repository identity sanitization/canonicalization
- resumable context metadata
- Phase 28 CLI parser coverage

CI #525 exposed two real implementation defects and they were corrected rather than suppressed: JSON arrays were not normalized back to typed tuple fields, and SSH repository identity canonicalization did not strip the `git@` transport prefix. CI #526 then passed with all **341 tests** green.

## Deliberate non-goals

Phase 28 does not implement automatic remote synchronization, cloud storage, conflict-free replicated state, cross-environment process migration, live memory replication, credential migration, automatic Git push/pull, Codespace creation, or a new provider/model router. Transfer remains an explicit operator action using a portable artifact.
