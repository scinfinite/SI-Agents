# Phase 22 — Universal Harness Integration

**Status: Complete — CI verified as part of the post-v2 interoperability baseline.**

Phase 22 turned the Phase 17 harness boundary into a reusable, language-neutral integration surface without making SI-Agents depend on a specific external harness. Phase 21 remains the organization/team execution layer; Phase 22 supplies the bridge that exposes that organization to harness adapters.

## Delivered

- `core/runtime/wire.py` — `si.runtime.v1` serialization helpers and strict protocol-envelope validation.
- `core/runtime/bridge.py` — callback-based structural harness adapter bridge and metadata discovery.
- `core/runtime/deployment.py` — deterministic `HarnessDeploymentManifest` exposure description.
- Universal conformance coverage for correlation, terminal responses, cancellation, wire validation, and deterministic manifests.
- Preservation of governance, permissions, session isolation, and deny-by-default harness registration.

## Contract

The core remains authoritative for governance and permissions. A harness adapter is a transport boundary, not a security boundary. The existing `RuntimeEngine` requires an enabled registered harness, project/session identity where applicable, supported capabilities, and an allowed governance request before invoking an adapter.

The bridge accepts callbacks rather than importing SDKs. Vendor-specific adapters translate their native transport into the universal invocation contract and use the same conformance/governance boundary.

## Organization deployment

`HarnessDeploymentManifest` describes agents, teams, skills, required permissions, and capabilities for an external exposure surface. Required permissions are descriptive and are never automatically granted by manifest generation.

## Generalized external-reference lesson

External integration research reinforced the value of canonical contracts, adapter-specific projections, and a single source of truth. SI-Agents independently implemented those principles with typed governance boundaries.

## Verification

The completed Phase 22 acceptance gate included distribution build, isolated wheel installation/import, Ruff, the full pytest suite, universal harness tests, PR/mainline CI, and synchronized documentation.

## Historical boundary

The original Phase 22 document intentionally listed later harnesses, model gateways, environment installers, and other integrations as future work. Those concerns were implemented by later phases 23–29. They should not be interpreted as missing from the current repository.

## Current-state addendum

Current status is **Phase 29 complete** and Phase 30 is next. `PHASES.md` is authoritative for current implementation; this document remains the Phase 22 historical contract.
