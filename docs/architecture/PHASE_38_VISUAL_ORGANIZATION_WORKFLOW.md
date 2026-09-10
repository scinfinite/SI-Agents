# Phase 38 — Visual Organization & Workflow

**Status: Complete + CI verified.**

## Purpose

Phase 38 makes the SI organization inspectable as an interactive visual graph without moving authority into the browser. Operators can explore organizational ownership, workflow dependencies, Skills, capabilities, permissions, relationships, and current control-plane run state from the same canonical Control API.

## Delivered

- Deterministic `/api/v1/visualization` read model.
- Organization graph covering teams, divisions, and the canonical agent catalog.
- Workflow graph covering workflows, immutable steps, dependencies, and assigned agents/teams.
- Skills/security graph covering agent-to-Skill, capability, and permission relationships plus governance permission effects.
- Current run records included as control-plane state; downstream execution progress is explicitly not inferred.
- Dependency-free SVG browser visualization with organization, workflow, and Skills/security modes.
- Search/filtering, node selection/detail inspection, pan, zoom, reset, responsive layout, and keyboard activation.
- OpenAPI synchronization and regression coverage for determinism, relationship coverage, live run state, endpoint exposure, aggregate integration, and execution-boundary preservation.

## Authority and security boundary

The visualization is read-only. It does not create, edit, authorize, execute, schedule, cancel, or deploy anything. Governance remains the authorization authority; the Control API remains the machine-facing boundary; the browser remains a presentation client.

The graph is rendered with DOM/SVG APIs and text nodes. No CDN, external script/style, telemetry, or browser-side execution engine is introduced. Existing Web security headers, localhost-first binding, remote authentication, CORS allowlist, bounded mutations, and audit behavior remain unchanged.

## Verification

Phase 38 implementation was merged from PR #35 as squash commit `657530eefa41794fb425cd0fe38d2aced9bd316d`. Feature CI passed all build, wheel-install, repository-audit, Ruff, and pytest gates. Final mainline CI **#845** (`34508914827`) passed every repository gate on that exact implementation merge commit; setup, checkout, Python/tooling, distribution build, wheel installation, repository audit, Ruff, tests, diagnostics, and cleanup all completed successfully.

The implementation was therefore verified on `main` before this documentation closure. This documentation update itself must receive the same final mainline verification before the phase is considered fully closed.

## Phase boundary

Phase 38 provides visual inspection and navigation only. Agent editing/customization, detailed evidence timelines, terminal UI, harness deployment controls, and final integration remain later phases.
