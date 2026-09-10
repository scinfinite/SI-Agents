# Phase 38 — Visual Organization & Workflow

**Status: implementation in review; CI pending.**

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

The graph is rendered with DOM/SVG APIs and text nodes. No CDN, external script, inline script/style, telemetry, or browser-side execution engine is introduced. Existing Phase 36 Web security headers, localhost-first binding, remote authentication, CORS allowlist, bounded mutations, and audit behavior remain unchanged.

## Verification

Feature CI must pass distribution build, isolated wheel installation, repository audit, Ruff, and the full pytest suite. Mainline CI must pass the same gates on the final merge commit. The phase is not complete until documentation records the exact final main commit, CI run, and test count.

## Phase boundary

Phase 38 provides visual inspection and navigation only. Agent editing/customization, detailed evidence timelines, terminal UI, harness deployment controls, and final integration remain later phases.
