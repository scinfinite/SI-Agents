# Phase 23 — OpenCode Integration

## Objective

Provide a real OpenCode harness adapter on top of the Phase 22 universal runtime contract without making OpenCode an SI-Agents core dependency.

## Delivered

- `adapters/opencode/` provides a stdlib-only OpenCode headless-server adapter.
- The adapter targets OpenCode's documented HTTP server API rather than a provider API or model router.
- Session creation and session reuse are supported.
- Synchronous message invocation is normalized into the SI runtime response/event contract.
- OpenCode session abort is mapped to the universal cancellation boundary, with request-to-session tracking.
- Optional OpenCode HTTP basic authentication is supported without persisting credentials.
- Model and agent selection can be passed through normalized invocation metadata.
- The adapter advertises its actual capability boundary: session continuity, tool calls, structured output, and cancellation are supported; streaming is intentionally fail-closed until an event-stream implementation is added.
- OpenCode SDKs are not added as Python dependencies; transport integration uses the standard library.

## Security and governance boundaries

- The adapter does not decide whether an action is allowed.
- The existing runtime registry remains deny-by-default.
- Phase 13 governance remains authoritative for execution decisions.
- OpenCode credentials remain outside SI-Agents; the adapter only receives an in-memory password when explicitly configured.
- The adapter never writes OpenCode configuration, credentials, or provider secrets.
- A deployment or adapter cannot grant permissions merely by being registered.

## Current OpenCode contract

OpenCode documents a headless server started with `opencode serve`, with a default local listener at `127.0.0.1:4096`. Its HTTP API provides session creation, synchronous session messages, asynchronous prompts, and session abort. Phase 23 uses the synchronous message and abort endpoints because they map cleanly to the current SI runtime contract.

## Explicit non-goals

Phase 23 does not implement OmniRoute/model routing, Termux/Codespace setup, automatic installation, a general `si` CLI, or adapters for other harnesses. It also does not claim streaming support where the adapter does not yet normalize OpenCode's event stream.

## Verification

Acceptance coverage includes metadata/capability declaration, configuration validation, new-session invocation, existing-session reuse, HTTP failure classification, and cancellation. CI must additionally verify build, isolated wheel installation/import, Ruff, and the complete test suite before Phase 23 is declared complete.
