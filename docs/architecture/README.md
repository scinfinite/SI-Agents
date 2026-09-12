# Architecture

SI-Agents V4 uses a single authoritative SI Core. Web, TUI, CLI, OpenCode, runtime adapters, schedulers, agents, teams, workflows, and integrations are clients/adapters of that authority rather than independent state owners.

## V4 target architecture

```text
OpenCode / Web / TUI / CLI → SI Core / Control API
                          → Scheduler / Orchestrator
                          → Tasks / Agents / Teams / Workflows
                          → Capability Authorization → OmniRoute
                          → Models / Providers / APIs
                          → Results / Artifacts / Evidence
                          → Observability → Evaluation → Continuous Improvement
                          → Cross-Runtime Gateway → Ecosystem / Marketplace → Clients / Harnesses
```

OmniRoute owns model/provider/API routing. SI Core owns execution, orchestration, governance, evidence, lifecycle, persistence, recovery, waiting, workspaces, observability, evaluation, continuous improvement, and cross-runtime governance.

## Verified V4 phases

Phases 44–63 are closed. Phases 46, 47, 49, 50, 58, 59, and 60 are advanced-hardened.

## Phase 63 architecture

Phase 63 provides governed ecosystem metadata and lifecycle contracts through `MarketplaceManifest`, `MarketplaceRegistry`, and `EcosystemManager`. Manifests cover strict versions, dependencies, compatibility, declared permissions, provenance/trust, payload identity, and deterministic manifest identity. Registry support covers deterministic package versions and templates; lifecycle support covers install, update, uninstall, rollback, bounded history, and drift detection.

Governance is deny-by-default for untrusted packages and requested permissions. Governance approval is bound to the exact manifest digest. Marketplace operations never grant execution authority or bypass SI Core authorization.

## Phase 63 closure evidence

- PR #77 merged into `main` as `19be0c14774e7073871a21fde42132a73c2a77d4`.
- PR CI #1189 / `34694186010` passed wheel verification, repository audit, integration verification, Ruff, and full pytest.
- Final documentation-synchronized mainline CI is the authoritative exact-tree closure gate.

## Current position

**Phase 63 is complete. Phase 64 — SDK / Developer Platform follows.**
