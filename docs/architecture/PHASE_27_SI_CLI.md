# Phase 27 — `si` CLI + Easy Setup

**Status: Complete and CI-verified.**

## Objective

Phase 27 adds the first user-facing control surface for SI-Agents. The `si` executable exposes environment diagnosis, status, canonical organization/workflow discovery, explicit setup, package update, and governed team execution without making the CLI a hidden policy or provider authority.

## Commands

```text
si doctor [--json]
si status
si agents
si teams
si setup [--apply] [--install-opencode] [--configure-opencode] [--opencode-url URL] [--omniroute-url URL] [--model MODEL]
si update [--apply]
si run TEAM --objective TEXT
```

### Read-only surfaces

`doctor`, `status`, `agents`, and `teams` are read-only. They delegate to existing runtime/catalog contracts and do not become a second policy system.

### `setup`

Default behavior is a dry-run plan. `--apply` is required before local mutation. Only explicit allowlisted environment/setup actions may execute; arbitrary shell strings are rejected. OpenCode configuration changes are narrow, parse-safe, and never persist SI copies of credentials.

### `update`

Default behavior is a dry-run package upgrade plan. `--apply` explicitly invokes the approved package upgrade command.

### `run`

Executes an existing canonical team through `TeamEngine` and the existing agent worker/runtime governance. The CLI does not grant permissions or bypass governance.

## Configuration and security

The CLI stores only non-secret configuration at `~/.config/si-agents/config.json` by default (or `SI_CONFIG`) using atomic replacement and restrictive permissions. No API key, password, provider credential, or OpenCode auth token is stored by Phase 27.

OmniRoute remains the model/provider routing authority and OpenCode remains the harness/credential authority.

## Verification evidence

The final Phase 27 verification recorded distribution build, isolated wheel installation, packaged catalog smoke tests, Ruff, and the complete pytest suite with **331 tests**. Earlier CI defects were fixed and rerun rather than suppressed.

## Current-state addendum

Phase 28 later added `si handoff create|inspect|import` and optional `--handoff` workflow continuation. Phase 29 later added deterministic persona discovery/validation/compilation. The Phase 27 CLI contract remains the foundation for those later commands. Current status is Phase 29 complete and Phase 30 is next.
