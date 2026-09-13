# Phase 64 — SDK / Developer Platform

## Status

**Complete.** Phase 64 is merged through PR #78 and its implementation was validated by the repository SDK and mainline gates. Its synchronized documentation is now maintained as part of the V4 documentation baseline.

## Purpose

Phase 64 turns the versioned Control API into a stable developer surface without moving authority out of SI Core. Python and TypeScript/JavaScript clients are adapters: governance, execution, authorization, persistence, and evidence remain owned by SI Core.

## Delivered surface

### Typed SDKs

- `sdk/python/si_agents` — dependency-free Python client with typed dataclasses and stable `ApiException` failures.
- `sdk/typescript` — strict TypeScript package with generated declaration output and browser/Node-compatible Fetch, SSE, and WebSocket primitives.
- Both clients pin requests to `/api/v1`, never put bearer credentials into URLs, and expose bounded concurrency helpers.

### REST contracts

- Existing Control API remains transport-neutral and versioned at `/api/v1`.
- SDK list operations support bounded `limit`, opaque cursor pagination, free-text query, and exact public-field filters.
- Cursors are cryptographically fingerprinted to the query/filter set; a cursor cannot be replayed against a different filter set.
- Stable JSON errors contain `error`, `message`, and `request_id` and are mapped to typed SDK exceptions.

### Authentication and identity

- Optional server bearer authentication is configured with `create_server(..., auth_token=...)` or `SI_API_TOKEN`.
- Missing/incorrect bearer credentials fail closed with HTTP 403 when authentication is configured.
- Approval identity remains separately bound to `X-SI-Subject` and `X-SI-Project`.
- Credentials are never accepted as query parameters by the SDK.

### Idempotency and concurrency

- `X-Idempotency-Key` is supported for run creation with a bounded replay cache.
- Client concurrency is explicitly bounded rather than spawning unbounded request fan-out.
- Idempotent replay returns the original run payload instead of creating a second control-plane run.

### Event subscriptions

- `/api/v1/events/stream` exposes server-sent events with bounded stream lifetime and heartbeat frames.
- `/api/v1/events/ws` provides a WebSocket event transport for SDK consumers.
- `/api/v1/subscriptions` registers explicit SSE or webhook subscriptions; deletion is explicit and returns 204.
- Webhook registration validates URL schemes, rejects embedded credentials, requires HTTPS for remote targets, and signs deliveries with HMAC-SHA256 when delivery is used.
- Subscription state does not grant execution capability.

### CI/CD and reference tooling

The SDK is packaged with the Python distribution, while the TypeScript package contains its own strict build/check metadata. A dedicated SDK workflow validates Python compilation/tests and strict TypeScript checking/building. The repository closure gate remains authoritative for compileall, Ruff, pytest, wheel verification, audit, and integration verification.

## Security invariants

1. SDKs never become policy or execution authorities.
2. Authentication is header-only; tokens are not serialized into URLs.
3. Pagination cursors are opaque, bounded, and bound to their original filter/query set.
4. Request bodies remain subject to the existing Control API limit.
5. Idempotency keys are bounded and replay only within the server instance/cache scope.
6. Webhook secrets are returned only at registration time and are not exposed by subscription listing.
7. Remote webhook targets require HTTPS; loopback HTTP is reserved for local development.
8. Event streaming is observational; it does not infer execution state or authorize actions.

## Reference patterns

Phase 64 uses broadly known engineering patterns—typed interfaces, bounded operations, explicit integration boundaries, reproducible developer entry points, security-first defaults, and specialized workflow surfaces—without copying another project's implementation, prompts, branding, or distinctive expressive material.

## Closure evidence

- Phase 63 was verified merged into `main` before Phase 64 began.
- PR #78 was merged into `main` after the implementation gate.
- The Phase 64 implementation-tree closure was validated during the Phase 65 cycle by CI #1239 / `34697885027`, which passed distribution build, wheel installation, repository audit, integration verification, Ruff, and full pytest on the resulting `main` tree.
- Phase 65 is now the completed workflow/automation layer and Phase 66 is the next roadmap phase.
