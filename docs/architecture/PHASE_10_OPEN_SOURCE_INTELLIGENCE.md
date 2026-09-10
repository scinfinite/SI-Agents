# Phase 10 — Open-Source Intelligence

## Status

**Complete — implementation and CI verified.**

## Goal

Give SI-Agents a provenance-preserving, read-oriented intelligence layer for studying external repositories without treating external content as instructions or silently granting permissions.

## Delivered

- Repository metadata model and registry.
- Repository archaeology and deterministic history summaries.
- Structured commit, issue, and pull-request observations.
- Release tracking model.
- Security-advisory model for vulnerability observations.
- Conservative SPDX/license assessment with fail-closed unknown handling.
- Project-health assessment based only on supplied observable signals.
- Freshness/staleness detection.
- Read-only provider contract with dependency injection; network access is not hidden inside the intelligence layer.
- Provenance-bearing snapshots and duplicate-safe storage.
- Explicit limitations when information is missing.

## Architecture

```text
External repository/provider
        |
        v
Read-only provider contract
        |
        v
OpenSourceSnapshot
  |       |       |
history  issues  PRs/releases/security
        |
        v
license + health + freshness analysis
        |
        v
provenance-bearing intelligence result
```

## Safety and legal boundaries

External repository data is untrusted research input. It is never interpreted as SI-Agents policy or system instructions. Collection is read-only at the provider contract level. Repository mutation, command execution, credential operations, and publication remain controlled by existing permission and approval systems.

License identifiers are signals, not legal conclusions. Unknown licenses remain unknown, and even a recognized permissive SPDX identifier requires review of the actual license text and applicable terms. This subsystem does not provide legal advice.

## Verification

Tests cover repository/history/issues/PRs/releases/security models, provider provenance, duplicate protection, deterministic archaeology, health limitations, stale snapshots, license fail-closed behavior, provenance requirements, and score validation.

The CI acceptance requirement is: build succeeds, Ruff succeeds, and the complete pytest suite succeeds on the final repository head. Any failure found while completing this phase must be fixed and rerun before declaring completion.
