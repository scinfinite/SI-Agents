# Phase 63 — Ecosystem / Marketplace

## Status

**Complete.** Implementation is merged, adversarial tests are green, documentation is synchronized, and final exact-tree mainline CI is green.

## Contract

Phase 63 introduces a governed ecosystem metadata and lifecycle layer for agents, skills, tools, teams, workflows, model/provider profiles, and future MCP extensions. `MarketplaceManifest` provides strict versions, dependencies, compatibility declarations, permission declarations, provenance/trust, payload identity, and deterministic manifest identity.

`MarketplaceRegistry` provides deterministic version lookup and governed templates. `EcosystemManager` provides install, update, uninstall, rollback, bounded lifecycle history, and drift detection.

## Governance and authority invariants

- Marketplace registration and installation never grant execution authority.
- Compatibility is checked before lifecycle activation.
- Requested permissions must be explicitly declared by the manifest.
- Untrusted packages require an explicit governance hook.
- Governance approval is bound to the exact manifest digest.
- Dependencies must already be installed at or above their declared minimum version.
- Updates must strictly increase the package version.
- Rollback targets a previously recorded version and is governance-checked again.
- Manifest integrity covers all security-relevant metadata, including description and artifact/payload identity.
- Lifecycle history is bounded to prevent unbounded memory growth.
- Drift detection compares the installed manifest identity with the current registry metadata.
- The marketplace stores metadata/lifecycle state only; SI Core remains authoritative for authorization and execution.

## Verification

Dedicated adversarial coverage is in `tests/unit/test_phase63_marketplace.py`, covering strict versions, duplicate protection, compatibility, trust, permissions, exact-digest governance, dependencies, update/rollback/uninstall lifecycle, bounded history, drift detection, templates, and malformed metadata.

Closure evidence:

- Phase 62 was verified closed on `main` before Phase 63 began.
- PR #77 merged into `main` as `19be0c14774e7073871a21fde42132a73c2a77d4`.
- PR CI #1189 / run `34694186010` passed the complete repository gate after the integrity-digest hardening fix.
- Final documentation-synchronized mainline CI is required before phase closure.

**Phase 64 — SDK / Developer Platform is next.**
