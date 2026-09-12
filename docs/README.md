# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–63**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened. **Phase 62 — Cross-Runtime / Cross-Harness and Phase 63 — Ecosystem / Marketplace are fully implemented, audited, documented, merged, and verified by mainline CI.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap, `architecture/README.md` for the current architecture summary, `architecture/PHASES.md` for phase evidence, and `architecture/PHASE_63_ECOSYSTEM_MARKETPLACE.md` for the Phase 63 contract.

## Phase 63 — Ecosystem / Marketplace

Phase 63 provides strict versioned marketplace manifests, dependency and compatibility declarations, explicit permission declarations, provenance/trust, exact manifest identity, deterministic package/template registries, governed install/update/uninstall/rollback lifecycle, bounded history, and drift detection.

Marketplace lifecycle is metadata/state management only. Installation never grants execution permission; untrusted packages require explicit governance, and governance approval is bound to the exact manifest digest. SI Core remains authoritative for authorization and execution.

## Closure evidence

- Phase 61: merged PR #75 / PR CI #1157 (`34692165853`).
- Phase 62: merged PR #76 as `607085782a75e31a60774afe975edcbd38bf5e4c`; final mainline CI #1186 (`34693756693`) green.
- Phase 63: merged PR #77 as `19be0c14774e7073871a21fde42132a73c2a77d4`; PR CI #1189 (`34694186010`) green.
- Final documentation-synchronized mainline CI for the completed Phase 63 tree is the authoritative closure verification.

## V4 product surfaces

Web, TUI, CLI, OpenCode, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next phase

**Phase 64 — SDK / Developer Platform.**

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
