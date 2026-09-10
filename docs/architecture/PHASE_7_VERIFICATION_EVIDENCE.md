# Phase 7 — Verification + Evidence

**Status: Complete — implementation and CI verified.**

## Purpose

Phase 7 makes verification a first-class control-plane capability. SI-Agents must distinguish a claim from the evidence supporting it, fail closed when verification is missing or broken, actively attempt to falsify results, and expose release-readiness gates.

## Implemented capabilities

### Claims

`core/verification/claims.py` defines bounded claims with:

- statement and scope
- explicit acceptance criteria
- linked evidence IDs
- confidence
- immutable identifiers and timestamps

`ClaimStore` provides duplicate-safe registration and immutable-style evidence attachment.

### Evidence

`Evidence` is immutable and records:

- claim
- source
- verification status
- evidence kind
- optional task correlation
- details
- identifier and timestamp

`EvidenceStore` is append-only and supports exact-claim, verified, and failed evidence queries.

### Confidence

`core/verification/confidence.py` provides validated numeric confidence and low/medium/high levels. Confidence always has a human-readable rationale.

### Verification engine

`VerificationEngine` coordinates independent checks and produces a `VerificationReport`.

Rules:

- claims must be registered before verification
- zero checks produce `BLOCKED`
- checker exceptions become verification failures
- failed checks prevent a verified result
- supplied regression suites must pass
- supplied red-team suites must resist every attack
- a configured empty red-team suite is treated as blocked/failing
- evidence is recorded for each verification check
- no execution permission is granted by verification

### Regression

`RegressionSuite` runs deterministic regression cases and fails closed when a check returns false or raises. An empty suite is `BLOCKED` rather than silently passing.

### Red team

`RedTeamSuite` attempts to falsify a result. A successful attack or attack exception is a flaw. An empty configured suite is not considered a successful defense.

### Production readiness

`ProductionReadiness` and `ReadinessGate` provide an explicit release-readiness decision. Passed gates require evidence; failed gates require a reason. An empty gate set is blocked.

### Orchestrator integration

The control plane now exposes:

- `register_claim()`
- `verify_claim()`
- `evaluate_readiness()`

This keeps verification inside the same orchestration boundary as tasks, permissions, tools, skills, capabilities, and evidence.

## Verification layers

The Phase 7 model is deliberately layered:

```text
Claim
  ↓
Acceptance checks
  ↓
Evidence
  ↓
Regression
  ↓
Red team
  ↓
Confidence
  ↓
Production readiness
```

A successful command or test is evidence about one proposition; it is not automatically proof that the entire engineering task is complete.

## Acceptance criteria

- [x] Claims are explicit, bounded, and evidence-linkable.
- [x] Evidence is immutable and provenance-aware.
- [x] Verification fails closed on missing checks and checker exceptions.
- [x] Regression testing is first-class.
- [x] Red-team falsification is first-class.
- [x] Confidence is validated and justified.
- [x] Release-readiness gates require evidence.
- [x] Orchestrator integration preserves permission and execution boundaries.
- [x] Unit and integration tests cover success, failure, exception, empty-suite, and adversarial paths.
- [x] CI verifies build, lint, and tests before completion.

## Scope boundary

This phase provides the verification engine and evidence model. It does not claim that every future language, external service, model, security scanner, or production deployment is already verified. Those capabilities require their own evidence and are added in later phases.
