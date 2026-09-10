# Phase 35 — Control API

**Status: Complete + CI verified.**

## Goal

Phase 35 establishes the stable machine-facing Control API before the Web Control Center and TUI. Operator surfaces are clients of this API rather than independent authorities.

## Contract

The API is versioned under `/api/v1` and currently exposes:

- `GET /api/v1/health`
- `GET /api/v1/openapi.json`
- `GET /api/v1/agents`
- `GET /api/v1/teams`
- `GET /api/v1/workflows`
- `GET /api/v1/organization`
- `GET /api/v1/skills`
- `GET /api/v1/memory`
- `GET /api/v1/governance`
- `GET /api/v1/events`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}`
- `POST /api/v1/runs`

The POST operation is deliberately bounded: it evaluates the request through the existing `GovernanceEngine` and creates a queued run record only. It never executes an agent, workflow, Skill, tool, shell command, or external request.

## Architecture

```text
CLI / Web / TUI / Harness adapter
              │
              ▼
       Control API v1
              │
       ControlApiService
        ┌─────┼─────┐
        ▼     ▼     ▼
    Catalogs  Memory Governance
                    │
                    ▼
                 Decision
                    │
              ALLOW / DENY
                    │
              queued RunRecord
```

The API is a transport boundary over SI Core. It does not duplicate authorization, workflow scheduling, model routing, or memory persistence.

## Security boundary

- HTTP transport is dependency-free and localhost-first.
- Non-loopback hosts are rejected by the server factory.
- Mutation requests must use `application/json` and are capped at 1 MiB.
- Responses use `no-store`, `nosniff`, explicit JSON content type, and request-ID headers.
- No CORS allowance or browser credential handling is introduced by the transport.
- Governance decisions are authoritative; API clients cannot bypass them.
- Capability-bearing mutations require the existing scoped permission model.
- Credential-bearing external egress remains governed by Phase 33 and cannot be authorized by the API.
- API payloads contain metadata/read models, not secret values.

## Source-of-truth boundaries

- Agent identity comes from `config/agent-catalog.json`.
- Team identity comes from `config/team-catalog.json`.
- Organization workflows come from `config/organization-expansion.v1.json` and are validated against the agent catalog.
- Governance comes from `core.governance`.
- Memory remains owned by `core.memory`; the Phase 35 memory endpoint is intentionally a non-authoritative read-model placeholder until its persistence/query adapter is exposed through the API contract.

## Implementation

- `core/control_api/models.py` — version and immutable API/run/event contracts.
- `core/control_api/service.py` — transport-neutral API service and governed mutation boundary.
- `core/control_api/server.py` — dependency-free localhost HTTP transport.
- `core/control_api/openapi.py` — deterministic API description.
- `core/control_api/cli.py` — `si-api` localhost launcher.
- `tests/test_phase35_control_api.py` — contract, HTTP, governance, and adversarial tests.

## Design constraints

The API is intentionally smaller than a full Web backend. Phase 35 establishes the stable boundary; later phases add the UI and richer state surfaces without changing the authority model.

The API does not:

- execute arbitrary commands;
- expose secrets or credentials;
- accept remote binding;
- grant permissions through organization metadata;
- replace OmniRoute model/provider routing;
- create a second workflow scheduler;
- silently mutate persistent configuration.

## Final verification record

Phase 35 implementation was merged through **PR #27** as merge commit `8e990f225b69fe1822861e1f21af29094c6b481b`.

Feature CI **#809** passed distribution build/wheel verification, repository audit, Ruff, and the full pytest suite: **417 passed**.

The feature CI cycle caught and fixed Ruff import-order findings before the successful run. No test suite was accepted before those lint failures were resolved.

After merge, final mainline CI verification was run on the documentation-closed `main` state. That final green run is the release gate for Phase 35.

This phase is complete because implementation, security/adversarial tests, packaging, documentation synchronization, merge, and final mainline CI all passed.
