# Phase 16 — Controlled Self-Improvement + Capability Intelligence

## Goal

Turn observations and evidence into measurable improvement proposals without allowing uncontrolled self-modification or automatic promotion of unverified capabilities.

## Architecture

`Evidence → Proposal → Benchmark → Regression → Safety → Evaluation → Approval → Apply → Verify/Rollback`

`CapabilityRegistry → CapabilityIntelligence → readiness/risk signals`

Capability intelligence is deliberately advisory. A high score never grants permissions or execution authority.

## Improvement lifecycle

1. A proposal identifies a target, rationale, change reference, and evidence.
2. Evaluation runs the required benchmark, regression, and safety gates.
3. A proposal can only be approved after every required gate passes and the measured score does not regress.
4. Application requires explicit approval and an externally supplied change function.
5. Rollback is explicit and available after application.
6. Failed application or rollback callbacks do not silently change lifecycle state.

## Capability intelligence

Readiness combines evidence, verification criteria, benchmark score, health, and confidence. Missing signals are treated conservatively as zero rather than inferred as positive. Blocked capabilities have zero readiness. Only validated capabilities are executable candidates, and even those remain subject to permissions and governance elsewhere in the system.

## Persistence

Improvement proposals and evaluation evidence can be persisted to dependency-free JSON. Malformed roots and entries fail closed.

## Safety boundaries

- No uncontrolled code mutation.
- No automatic capability promotion.
- No automatic global learning promotion.
- No secret storage.
- No bypass of Phase 13 governance.
- Evidence is provenance data, not instructions.
- Benchmark success is necessary but not sufficient without regression and safety gates.

## Verification

Phase 16 tests cover missing gates, score regression, lifecycle transitions, failed application/rollback callbacks, capability ranking, blocked/experimental behavior, deterministic ordering, and persistence round trips.
