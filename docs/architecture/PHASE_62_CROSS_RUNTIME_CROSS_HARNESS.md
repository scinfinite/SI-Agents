# Phase 62 — Cross-Runtime / Cross-Harness

## Status

**Implemented and merged; final synchronized-tree mainline CI closure pending.**

Phase 62 establishes a harness-neutral interoperability layer without creating a second execution authority. Existing SI Core remains authoritative for execution, sessions, capabilities, security, evidence, workspaces, evaluation, and continuous improvement.

## Contract

The portable boundary covers runtime, session, tool, model, event, capability, context, checkpoint, and artifact resource families through `PortableAdapterDescriptor`, `PortableAdapter`, and `PortableAdapterRegistry`. The registry is deny-by-default and discovery-only.

Harnesses implement `HarnessAdapter`. `CrossRuntimeGateway` provides deterministic discovery, streaming capability filtering, preferred selection, health probing, bounded degradation/quarantine/recovery, project+harness session binding, explicit session migration, and safe pre-start fallback.

## Security and authority invariants

- Registration/discovery never grants execution capability.
- Disabled or quarantined harnesses are never selected.
- Session identity is bound to project and harness; mismatches fail closed.
- Migration is explicit and creates a replacement session.
- Fallback is prohibited after `started`, `delta`, `tool_call`, or `tool_result` events.
- Request input is excluded from route-decision fingerprints.
- Health failure counts and quarantine duration are bounded.
- Transport failures do not become authorization grants.
- Runtime authorization remains outside the gateway.

## Compatibility

Existing OpenCode, OmniRoute, local harness, runtime engine, session, wire protocol, checkpoint, and deployment contracts remain valid. OpenCode is a supported harness, not the runtime definition.

## Verification

Dedicated adversarial coverage is in `tests/unit/test_phase62_cross_runtime.py`, covering deterministic discovery, capability filtering, safe/unsafe fallback, quarantine/recovery, session isolation, explicit migration, deny-by-default selection, all portable resource kinds, duplicate protection, and non-secret decision fingerprints.

Closure evidence so far:

- PR #76 merged into `main` as `607085782a75e31a60774afe975edcbd38bf5e4c`.
- PR CI #1166 / run `34692621358` passed repository audit, integration verification, Ruff, wheel verification, and full pytest.
- Final synchronized-tree mainline CI remains the authoritative closure gate.

**Phase 63 — Ecosystem / Marketplace is next after this closure gate.**
