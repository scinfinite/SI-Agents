# Phase 23 — OpenCode Integration

**Status: Complete — implementation and CI verified.**

## Objective

Provide a real OpenCode harness adapter on top of the Phase 22 universal runtime contract without making OpenCode an SI-Agents core dependency.

## Delivered

- `adapters/opencode/` provides a stdlib-only OpenCode headless-server adapter.
- The adapter targets OpenCode's documented HTTP server API rather than a provider API or model router.
- Session creation and session reuse are supported.
- Synchronous message invocation is normalized into the SI runtime response/event contract.
- OpenCode session abort is mapped to the universal cancellation boundary.
- Optional OpenCode HTTP basic authentication is supported without persisting credentials.
- Model and agent selection can be passed through normalized invocation metadata.
- The adapter advertises its actual capability boundary and fails closed for unsupported streaming.
- OpenCode SDKs are not added as Python dependencies.

## Security and governance boundaries

The adapter does not decide whether an action is allowed. The runtime registry remains deny-by-default, Phase 13 governance remains authoritative, and OpenCode credentials remain outside SI-Agents. The adapter never writes OpenCode configuration, credentials, or provider secrets. Registration cannot grant permissions.

## Current OpenCode contract

OpenCode provides a headless server and HTTP API for sessions, messages, abort, and events. Phase 23 uses the synchronous message and abort endpoints that map to the SI runtime contract; unsupported event-stream behavior remains explicitly fail-closed until normalized by a future implementation.

## Verification

Phase 23 acceptance includes metadata/capability declaration, configuration validation, new-session invocation, existing-session reuse, HTTP failure classification, and cancellation, with repository distribution build, isolated wheel installation/import, Ruff, and full pytest verification.

## Current-state addendum

Later phases built the OmniRoute delegation boundary, Termux/Codespaces readiness, the `si` CLI, cross-environment handoff, and persona layer around this adapter. OpenCode remains the harness boundary; OmniRoute remains model/provider routing authority. Current status is Phase 29 complete and Phase 30 is next.
