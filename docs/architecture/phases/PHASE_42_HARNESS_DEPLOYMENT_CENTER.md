# Phase 42 — Harness Deployment Center

## Status

**Complete and CI-verified.**

## Purpose

Phase 42 adds a governed, inspectable deployment-planning boundary between the SI organization and registered harness adapters. It describes deployment targets and prepares deterministic manifests without making deployment itself an authority.

## Contract

- `core/deployment_center/` owns immutable deployment-plan and target contracts.
- Registered adapter directories are discoverable as targets; runtime health is not inferred from directory presence.
- Plans are deterministic and explicitly `valid` or `blocked`.
- Unknown harness targets fail closed.
- Capability and permission requests are never granted by a deployment plan; authority-bearing requests are blocked until an existing governance path authorizes them.
- The existing `core/runtime/deployment.py` manifest remains a portable description. It does not enable an adapter or execute an agent.
- No credentials are copied, migrated, persisted, or transformed.
- No worker, Skill, workflow, shell command, tool, harness invocation, or external request occurs in the Deployment Center.
- There is deliberately no `apply` operation in the Phase 42 planning surface.

## Operator surfaces

- `si deploy targets --json` inspects registered targets.
- `si deploy plans --json` inspects plans created in the current process.
- `si deploy plan PLAN_ID HARNESS_ID --json` creates a planning record only.
- Web: `/deployments` provides the same inspection/planning boundary through the existing localhost-first Web server.
- API: `GET /api/v1/deployments` and `POST /api/v1/deployments` expose the deployment read/planning contract.

The Web and CLI surfaces do not duplicate governance or execution logic.

## Security

Deployment planning cannot grant permissions, capabilities, environments, credentials, network access, or execution authority. Mutation requests are bounded by the existing Web JSON body limit and audit metadata excludes request bodies. The Web surface retains localhost-first binding, authenticated remote opt-in, strict CSP, CORS allowlisting, and security headers.

## Verification

The Phase 42 implementation was merged through PR #46 as squash commit `70d5f96c15bfbf200804a50f43dc6e12f5dde903`. The first validation attempt exposed an OpenAPI syntax error during wheel installation; that defect was corrected, then Ruff exposed compact-handler style violations and tests exposed duplicate normalization plus an assertion mismatch. Those issues were fixed rather than suppressed in the test suite. Final feature/mainline validation on head `1043a7f53e358baa5a0672f7ff430d4737a80b28` passed distribution build, wheel installation, repository audit, Ruff, and the full pytest suite.

The final mainline verification after merge is required before documentation closure; this record is complete only when that run is green.

## Next phase

**Phase 43 — Final v3 Integration & Hardening.**
