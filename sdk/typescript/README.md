# @si-agents/sdk

Typed TypeScript client for the SI-Agents Control API v1.

## Quick start

```ts
import { SIClient } from "@si-agents/sdk";

const si = new SIClient({
  baseUrl: "http://127.0.0.1:8787",
  token: process.env.SI_API_TOKEN,
  subject: "ci",
  project: "example",
});

const health = await si.health();
const page = await si.list("agents", { limit: 25, query: "builder" });

await si.createRun(
  { action: "inspect", subject: "ci" },
  "stable-run-key-001", // safe retry / idempotency key
);

for await (const event of si.streamEvents()) {
  console.log(event.event_type, event.subject);
}
```

The SDK exposes typed REST calls, filter-bound cursor pagination, stable `SIError` failures, bearer auth, identity headers, idempotent run creation, bounded concurrency, SSE streaming, WebSocket event subscriptions, and subscription registration. Credentials are never placed in URLs.

## Design guarantees

- API paths are pinned to `/api/v1`.
- Pagination cursors are opaque and bound to their query/filter set.
- Concurrency is bounded to 32 workers maximum.
- Webhook/SSE subscriptions are explicit lifecycle resources.
- SI Core remains authoritative for governance and execution; the SDK is a client, not an authority.
