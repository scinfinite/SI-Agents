# Phase 37 — Control Center

**Status: complete + CI verified.**

## Purpose

Phase 37 turns the Phase 36 local Web foundation into a usable operator Control Center. The browser surface is a client of the versioned Control API and never becomes a second orchestration, execution, or governance authority.

## Delivered surface

The packaged single-page interface provides live views for:

- Overview — control-plane counts and authority boundary.
- Agents — canonical specialist catalog.
- Teams — operating teams and declared tasks.
- Workflows — workflow definitions and step counts.
- Skills — packaged `SKILL.md` inventory.
- Memory — scoped Memory read model.
- Knowledge — explicitly backed by the current Memory read model until a dedicated Knowledge presentation is available.
- Evidence — control-plane events and run-state evidence, without inventing downstream execution evidence.
- Runs — governed run records; creation remains queued-only.
- Organization — teams, divisions, assignments, and workflow topology.
- Governance — permissions, policies, and capabilities.
- Environments — sanitized current runtime context.
- Harnesses — registered adapter families from repository structure; runtime health is not inferred.
- Settings — effective API, Web, security, and execution-boundary settings.

The interface uses no CDN, external JavaScript, inline script, inline style, telemetry, or browser-side execution engine. It uses DOM text APIs rather than `innerHTML` for data rendering.

## Read-model extensions

The Control API service now exposes read-only views for `/api/v1/evidence`, `/api/v1/environments`, `/api/v1/harnesses`, `/api/v1/settings`, and `/api/v1/control-center`. These views are deterministic projections of existing state and sanitized runtime metadata.

The OpenAPI document is synchronized with the new read-only paths. No new mutation authority was introduced.

## Security boundary

- Existing Phase 36 localhost-first binding and authenticated remote opt-in remain unchanged.
- The browser sends same-origin requests and does not store credentials.
- CSP continues to allow only same-origin scripts/styles and same-origin API connections.
- The UI cannot execute an agent, tool, shell command, workflow, or external provider request.
- Run creation continues through `ControlApiService.create_run()`, which delegates authorization to the canonical Governance Engine and returns a queued record only.
- Environment reporting deliberately avoids exposing the process environment; it reports only non-secret runtime facts.
- Evidence reporting distinguishes control-plane evidence from downstream execution evidence.

## Verification

The Phase 37 regression suite covers:

- live read endpoints and no-store responses;
- non-executing Control Center settings;
- environment sanitization against secret-like process variables;
- registered-adapter read semantics;
- packaged HTML/JavaScript delivery;
- all required operator navigation labels;
- avoidance of unsafe `innerHTML` rendering;
- live run state after an accepted governed mutation.

Final mainline CI **#840** (`34507154878`) passed the repository distribution build, isolated wheel installation, repository audit, Ruff, and full pytest gates on main commit `d54ab5a0e9a0dc5daed72e89bdaf842b8da59078`, with **441 tests passed**. This is the authoritative final verification for the documentation-closed Phase 37 state.

## Phase boundary

Phase 37 establishes the operator Control Center foundation. It does not add visual organization/workflow editing, a graphical agent builder, evidence visualization beyond the existing read models, TUI parity, or execution/harness deployment controls; those remain later phases.
