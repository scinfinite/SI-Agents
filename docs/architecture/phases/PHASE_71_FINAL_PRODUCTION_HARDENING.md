# Phase 71 — Final Production Hardening

## Status

**Complete / 100% — implementation merged to canonical `main`; pre-merge full CI and SDK gates passed; synchronized documentation is on main; final post-merge mainline CI/SDK verification is the release gate.**

Phase 71 is the final V4 production-hardening gate. It closes lifecycle gaps at the authoritative SI runtime boundary without introducing a second execution or provider-routing authority.

## Hardened invariants

### Invocation lifecycle

- Every enabled-harness invocation is keyed by `(harness_id, request_id)`.
- A completed/failed/cancelled response is replayable for the lifetime of its bounded ledger entry.
- Reusing a request ID with a different immutable request payload fails closed with `invalid_request`.
- Concurrent duplicate requests cannot execute the same capability twice; a request already in progress is rejected.
- Cancellation is a terminal lifecycle state and cannot overwrite an already terminal response.
- The ledger is bounded to prevent unbounded in-process request-state growth.

### Authority and isolation

- `RuntimeEngine` remains the authoritative execution boundary.
- Harness adapters remain transport/execution adapters only.
- OmniRoute remains the model/provider routing boundary.
- Lifecycle keys include the harness ID so request IDs cannot accidentally replay across harness boundaries.
- Existing project/session isolation and governance checks remain before adapter execution.

## Validation coverage

`tests/integration/test_phase71_final_hardening.py` covers:

- idempotent replay;
- request-ID payload confusion;
- cross-harness request-ID isolation;
- terminal cancellation and replay;
- bounded lifecycle retention;
- concurrent duplicate execution prevention;
- invalid ledger configuration.

The existing full runtime, OpenCode, OmniRoute, Web/TUI/CLI, SDK, wheel, npm, repository-audit, Ruff, compileall, and full pytest gates remain mandatory.

During Phase 71 validation, the CI acceptance suite found and forced correction of two real defects before merge:

1. cancellation attempted to reference an unavailable request variable;
2. `core.runtime.models.RuntimeError` shadowed Python's built-in `RuntimeError`, so concurrent lifecycle contention could not be normalized correctly.

Both were fixed and the corrected tree passed full CI and SDK CI before merge.

## Merge and closure record

- PR: **#85**
- Merge commit: `d4555a6b2e9ca9daed3af4914d72461a6a5f3739`
- Pre-merge full CI: **#1375**, run `34743395331`, success
- Pre-merge SDK: **#167**, run `34743395251`, success
- Synchronized status documentation: `README.md`, `docs/architecture/PHASES.md`, `docs/architecture/SI_AGENTS_V4_PLAN.md`, and `SIA_SPECS.md`

## Final closure gate

The implementation is merged and documented on canonical `main`. Final release closure requires the exact synchronized mainline SHA to pass the full CI and SDK workflows, including repository audit, distribution/package verification, integration checks, Ruff, compileall, pytest, and SDK tests. The repository branch cleanup remains a post-merge housekeeping check where supported by repository permissions.
