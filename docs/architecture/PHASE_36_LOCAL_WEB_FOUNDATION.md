# Phase 36 — Local Web Foundation

## Status

**Complete + CI verified.**

Phase 36 establishes the first Web operator surface without creating a second SI authority. The Web layer is a transport and presentation boundary over the existing Control API and SI Core contracts.

## Delivered contract

- `core.web` provides a dependency-free HTTP foundation based on Python's standard library.
- The default bind is `127.0.0.1:8788`; localhost is the safe default and does not require authentication.
- `si web` is provided through the stable SI launcher and `si-web` is available as a direct launcher.
- The browser surface is packaged with the project and serves a minimal live health view plus Control API navigation.
- API reads reuse the existing Control API service, so Web does not duplicate agent, team, workflow, organization, Skill, Memory, event, run, or governance authority.
- JSON mutations are bounded to 1 MiB, require `application/json`, return safe error envelopes, and retain the Control API's governance decision boundary.
- Accepted run creation remains a queued Control API record; the Web server never executes agents, Skills, workflows, tools, commands, or external requests.

## Security boundary

Remote binding is opt-in. A non-loopback bind requires both `allow_remote=True` and a bearer token of at least 32 characters supplied through an environment variable by the launcher. Tokens are never placed in URLs or audit records.

CORS is deny-by-default. Only explicitly configured HTTP(S) origins are accepted; wildcard `*` is forbidden. The server emits a restrictive CSP, frame protection, MIME sniffing protection, no-referrer policy, permissions policy, and `no-store` caching. It does not enable browser credentials or introduce third-party scripts.

Mutations and request outcomes are written to a local JSONL audit file with restrictive permissions. Secret-like fields are recursively redacted. The server does not log request bodies verbatim and does not introduce telemetry.

SIGINT/SIGTERM are handled through a controlled server lifecycle so the HTTP worker is shut down and joined before the process exits.

## Verification

Phase 36 tests cover:

- default localhost binding
- explicit remote exposure requirements
- token length enforcement
- wildcard and unlisted CORS rejection
- static asset serving
- security headers
- live health API state
- safe 404 errors
- mutation content-type and size limits
- governance-denial response safety
- queued run creation
- authenticated remote access
- secret redaction and private audit-file permissions

The implementation was merged through PR #31 at merge commit `0829e29d7e2b3718e57caf027f9a1cb8534cbcba`. Feature CI run `34505281056` completed successfully after all build, wheel-install, repository-audit, Ruff, and pytest gates passed.

## Operator usage

From the repository root:

```bash
si web
```

Useful options include `--host`, `--port`, `--root`, `--allow-remote`, `--auth-token-env`, `--cors-origin`, and `--audit-log`.

For remote exposure, set a high-entropy `SI_WEB_AUTH_TOKEN` (or another explicitly selected environment variable), pass `--allow-remote`, and bind to the intended interface. Never put the token in shell history, source code, a URL, or a browser query parameter.

## Boundary for Phase 37

Phase 36 deliberately stops at the Web foundation. It does not attempt to implement the full Control Center. Phase 37 can build operator views, navigation, authentication UX, and richer live-state presentation on top of this boundary without moving authority into the Web layer.
