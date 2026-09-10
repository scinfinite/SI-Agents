# Phase 40 — Evidence & Observability

## Purpose

Phase 40 makes SI-Agents evidence-first at the inspection boundary: recorded claims are explicitly typed as facts, observations, inferences, or uncertainties; every record carries provenance, source, confidence, verification state, and optional run relationships.

The feature is intentionally an evidence record/read/write boundary, not an execution engine. Recording, verifying, superseding, or inspecting evidence never executes an agent, Skill, workflow, tool, shell command, harness, or external call.

## Contract

- `core/evidence/models.py` defines immutable `EvidenceRecord`, `EvidenceKind`, and `VerificationState` contracts.
- `core/evidence/store.py` provides schema-versioned local persistence with atomic replacement and restrictive `0600` permissions.
- `core/evidence/service.py` provides deterministic listing, detail, verification, and run-timeline projections.
- Verification states are explicit: `unverified`, `verified`, `contradicted`, and `superseded`.
- Uncertainty is first-class and cannot be marked verified.
- Confidence is bounded to `[0, 1]`.
- Supersession requires a known prior record and preserves the prior record as superseded rather than deleting it.
- Persisted timestamps are retained across reloads and records are ordered deterministically by creation time and ID.
- Runtime evidence state is stored under `.si/`, which is ignored by Git and is never part of the shipped repository state.

## Control API

The dependency-free Control API now exposes:

- `GET /api/v1/evidence` — existing control-plane evidence summary.
- `GET /api/v1/evidence/records` — persisted evidence records.
- `GET /api/v1/evidence/{evidence_id}` — one evidence record.
- `POST /api/v1/evidence` — record an evidence claim.
- `POST /api/v1/evidence/{evidence_id}/verify` — update verification state.
- `GET /api/v1/runs/{run_id}/timeline` — evidence timeline and typed/verification counts for a run.

The OpenAPI document is synchronized with these routes.

## Operator surface

A dependency-free packaged Evidence Explorer is available at `/assets/evidence.html`. It supports refresh and optional run-ID filtering and displays claim, kind, confidence, verification, source, run, and provenance. The main Control Center links to the explorer.

The browser remains a view over the Control API and does not gain execution authority. Static assets remain same-origin and CSP-compatible.

## Security and boundaries

- No request body is written to the Web audit log.
- Evidence persistence uses a restrictive local file mode and atomic replacement.
- Unknown evidence IDs fail closed with `404`.
- Invalid evidence payloads fail with bounded `400` responses.
- Invalid verification states are rejected.
- No credentials, environment secrets, or downstream execution state are inferred or exposed.
- Evidence is not treated as proof merely because it is recorded; verification state and provenance remain explicit.
- The Control API remains the machine-facing authority; Web remains a client/view.

## Verification

Phase 40 must be considered closed only after feature CI and the final documentation-closed mainline CI both pass build, wheel installation, repository audit, Ruff, full pytest, diagnostics, and cleanup gates.

## Next phase

**Phase 41 — TUI.**
