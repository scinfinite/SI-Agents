# Documentation

## Current V4 baseline

SI-Agents V4 has completed Phases **44–63**. Phases **46, 47, 49, 50, 58, 59, and 60** are advanced-hardened. **Phase 64 — SDK / Developer Platform is in implementation pending final exact-tree mainline CI.**

See `architecture/SI_AGENTS_V4_PLAN.md` for the authoritative roadmap, `architecture/README.md` for the current architecture summary, `architecture/PHASES.md` for phase evidence, and `architecture/PHASE_64_SDK_DEVELOPER_PLATFORM.md` for the current Phase 64 contract.

## Phase 64 — SDK / Developer Platform

Phase 64 provides typed Python and TypeScript SDKs, versioned REST access, stable errors, optional bearer authentication, header-bound identity, cursor pagination/filtering, idempotent run creation, bounded concurrency, SSE/WebSocket event transports, explicit SSE/webhook subscription lifecycle, signed webhook delivery primitives, OpenAPI updates, package metadata, examples, and dedicated SDK CI.

SDKs remain clients/adapters. SI Core remains authoritative for authorization, execution, evidence, lifecycle, persistence, and governance.

## Closed-phase evidence

- Phase 61: merged PR #75 / PR CI #1157 (`34692165853`).
- Phase 62: merged PR #76 as `607085782a75e31a60774afe975edcbd38bf5e4c`; final mainline CI #1186 (`34693756693`) green.
- Phase 63: merged PR #77 as `19be0c14774e7073871a21fde42132a73c2a77d4`; PR CI #1189 (`34694186010`) green; final exact-tree mainline CI #1198 (`34694418960`) green.

## V4 product surfaces

Web, TUI, CLI, OpenCode, SDKs, and future runtimes remain clients/adapters of one authoritative SI Core. No interface creates competing execution/session/wait/workspace/evaluation/improvement authority.

## Next closure target

**Phase 64 — SDK / Developer Platform.**

## Phase closure rule

A phase is not complete until implementation, unit/integration tests, adversarial/security tests, edge/failure tests, documentation synchronization, repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, and final exact-tree mainline CI are green.
