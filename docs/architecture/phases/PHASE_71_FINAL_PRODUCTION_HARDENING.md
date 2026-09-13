# Phase 71 — Final Production Hardening

## Status

**Implementation complete on the Phase 71 hardening branch; final status remains pending until the exact mainline CI and SDK gates are green.**

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

## Final closure gate

Phase 71 is not closed merely because the implementation tests pass. Closure requires:

1. the hardening tree is merged into canonical `main`;
2. only the canonical `main` branch remains after merge cleanup;
3. full CI is green on the exact final mainline SHA;
4. SDK CI is green on the exact final mainline SHA;
5. documentation and phase-status records identify Phase 71 as complete;
6. distribution, package, license/provenance, integration, security, and regression checks remain green.

Until those conditions are met, Phase 71 must be reported as **pending final verification**, not production-complete.
