# Phase 28 — Cross-environment & Handoff

**Status: Complete and CI-verified.**

## Objective

Phase 28 makes work portable between the supported Termux and GitHub Codespaces environments without turning either environment into a hidden state authority. A handoff is a signed-by-integrity, JSON-portable snapshot of workflow context, task state, results, checkpoints, and evidence references.

## Contract

The versioned envelope is `si.handoff.v1` and contains source/target environment, sanitized project identity, team/workflow execution identity, optional harness session identity, objective, task statuses/attempt counts, JSON-compatible workflow context, summarized agent results/evidence IDs, checkpoints, creation timestamp, and SHA-256 integrity digest.

The envelope contains no API keys, passwords, authorization headers, provider credentials, or secret-like fields. Secret-like keys are rejected recursively at creation and validation time.

## Commands

```text
si handoff create TEAM --objective TEXT --source termux|codespace --target termux|codespace --output FILE
si handoff inspect FILE
si handoff import FILE
si run TEAM --objective TEXT --handoff FILE
```

`create` executes the existing governed team and exports portable state. `inspect` verifies integrity before display. `import` verifies integrity, source/target compatibility, and workspace identity. `run --handoff` resumes validated context while still executing the canonical team through `TeamEngine` and normal governance.

## Governance boundary

Handoff state is data, not authority. Import cannot enable a harness, grant permissions, execute a command, install software, copy credentials, create accounts, change provider routing, or bypass approvals/governance. The target environment remains authoritative.

## Failure behavior

Unsupported schemas, malformed digests, secret-like context, same-environment handoffs, target mismatches, repository mismatches, and tampering are rejected. Handoff files are never executed as code.

## Verification evidence

Final mainline CI run **#526** passed distribution build, isolated wheel installation, installed catalog smoke tests, Ruff, and the full pytest suite with **341 passed**, including serialization, atomic storage, tamper detection, recursive secret rejection, target validation, repository identity canonicalization, resumable context, and CLI parser coverage.

## Current-state addendum

Phase 29 adds persona artifacts to the broader SI organization but does not change the handoff authority model. Persona files and handoff files remain data; neither grants permissions or executes imported content. Current status is Phase 29 complete and Phase 30 is next.
