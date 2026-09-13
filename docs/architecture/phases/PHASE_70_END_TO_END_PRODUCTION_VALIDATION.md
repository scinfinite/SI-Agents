# Phase 70 — End-to-End Production Validation

**Status: Complete / 100%**

## Objective

Validate the production path without introducing a second execution authority:

`OpenCode → SI Core/runtime → OmniRoute → model/provider boundary → SI Core/runtime → OpenCode`

Phase 70 also validates failure containment, governance, session isolation, model fallback, cancellation boundaries, distribution/install behavior, artifacts/evidence, and the existing Web/TUI/CLI/SDK regression surface.

## Acceptance coverage

- OpenCode session creation and message flow through a real local HTTP server.
- SI RuntimeEngine remains the authoritative execution/governance boundary.
- OmniRoute model discovery and completion invocation use a deterministic in-process transport for repeatable CI.
- Model preference/fallback selection is verified.
- Governance denial prevents downstream provider execution.
- Session/project isolation prevents cross-project execution.
- Cancellation remains harness-scoped; unsupported downstream cancellation is surfaced as a bounded failure.
- Existing OpenCode adapter retry/error mapping remains covered by the baseline adapter tests.
- Existing RuntimeEngine and SDK integration suites remain part of the final CI gate.
- npm distribution verification runs in CI, including package-content, version/license, and launcher smoke checks.
- Python wheel build/install and SI CLI smoke checks remain part of the same CI gate.
- Ruff, compileall, full pytest, repository audit, and SI integration verification remain mandatory.

## Deterministic boundary strategy

Phase 70 does not require live third-party model/provider credentials in CI. The test uses a deterministic OmniRoute transport and a localhost OpenCode-compatible HTTP server while exercising the actual SI RuntimeEngine, OpenCode adapter, and OmniRoute bridge contracts. This proves the control/data path and its failure boundaries without making CI dependent on external availability, accounts, billing, or secrets.

## Production checklist

| Area | Result |
| --- | --- |
| OpenCode → SI path | PASS |
| SI → OmniRoute path | PASS |
| OmniRoute → model/provider boundary | PASS (deterministic contract transport) |
| Result return to OpenCode | PASS |
| Governance denial | PASS |
| Session isolation | PASS |
| Model fallback | PASS |
| Cancellation boundary | PASS |
| Existing runtime E2E | PASS |
| npm distribution verification | PASS |
| Python wheel verification | PASS |
| Repository audit | PASS |
| Integration verification | PASS |
| Ruff | PASS |
| compileall | PASS |
| full pytest | PASS |
| SDK CI | PASS |

## Evidence

Primary Phase 70 acceptance coverage:

- `tests/integration/test_phase70_production_path.py`
- `tests/integration/test_runtime_e2e.py`
- `tests/test_opencode_adapter.py`
- `tests/test_omniroute.py`
- `tests/test_cli.py`
- existing Web/TUI/CLI/SDK test suites

Phase 70 closure requires final mainline CI to be green on the exact final `main` SHA after documentation and test changes.
