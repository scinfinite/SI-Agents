# Phase 64 — SDK / Developer Platform

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
- Client concurrency is explicitly bounded (maximum 32 workers) rather than spawning unbounded request fan-out.
- Idempotent replay returns the original run payload instead of creating a second control-plane run.

### Event subscriptions

- `/api/v1/events/stream` exposes server-sent events with bounded stream lifetime and heartbeat frames.
- `/api/v1/events/ws` provides a WebSocket event transport for SDK consumers.
- `/api/v1/subscriptions` registers explicit SSE or webhook subscriptions; deletion is explicit and returns 204.
- Webhook registration validates URL schemes, rejects embedded credentials, requires HTTPS for remote targets, and signs deliveries with HMAC-SHA256 when delivery is used.
- Subscription state does not grant execution capability.

### CI/CD and reference tooling

The SDK is packaged with the Python distribution, while the TypeScript package contains its own strict build/check metadata. The Phase 64 test suite covers cursor binding, filtering, pagination, auth failures, idempotent replay, subscription registration, and stable Python error mapping. The existing repository closure gate remains authoritative for compileall, Ruff, pytest, wheel verification, audit, and integration verification.

## Security invariants

1. SDKs never become policy or execution authorities.
2. Authentication is header-only; tokens are not serialized into URLs.
3. Pagination cursors are opaque, bounded, and bound to their original filter/query set.
4. Request bodies remain subject to the existing 1 MiB Control API limit.
5. Idempotency keys are bounded and replay only within the server instance/cache scope.
6. Webhook secrets are returned only at registration time and are not exposed by subscription listing.
7. Remote webhook targets require HTTPS; loopback HTTP is reserved for local development.
8. Event streaming is observational; it does not infer execution state or authorize actions.

## Reference patterns

Current ECC emphasizes security-first, research-first agent tooling and broad multi-harness developer workflows; current Agency Agents emphasizes specialized agents, repeatable workflows, explicit deliverables, and tool-specific installation paths. Phase 64 generalizes those principles into a neutral SDK contract: typed interfaces, bounded operations, explicit integration boundaries, and reproducible developer entry points rather than copying either project's implementation or prompts.

## Closure evidence

- Phase 63 was verified merged into `main` before Phase 64 began.
- PR #78 contains the Phase 64 implementation and test surface.
- Closure requires a green PR gate followed by a final exact-tree `main` CI run after documentation synchronization.
