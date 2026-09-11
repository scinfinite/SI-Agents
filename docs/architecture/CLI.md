# SI CLI

The `si` command is the operator-facing control surface for SI-Agents. It is a view over the canonical SI Core and typed registries; it is not a second policy authority.

## Current status

The v3 CLI is implemented and verified. The richer task/run/workflow/model/operator command tree described below is a **v4 target** and must not be treated as already implemented until its corresponding phases are complete.

## Current read-only diagnostics

```text
si doctor [--json]
si status [--json]
si audit [--json]
si verify [--json]
```

`si audit` and `si verify` are deterministic verification surfaces. They do not grant downstream execution authority.

## Current discovery

```text
si agents [--division DIVISION] [--status STATUS] [--search TEXT] [--json]
si personas [--division DIVISION] [--search TEXT] [--json]
si teams [--search TEXT] [--json]
```

`agents` reads the authoritative typed catalog. `personas` reads behavioral Markdown through the governed persona registry. These sources are intentionally distinct.

## Current setup and updates

```text
si setup [--apply] [--install-opencode] [--configure-opencode] [--model MODEL]
si update [--apply]
```

Setup is dry-run by default. `--apply` is required for mutation. Setup commands are allowlisted; SI does not accept arbitrary shell strings as setup input. Credentials are not stored by SI-Agents.

## Current governed execution

```text
si run TEAM --objective TEXT [--handoff FILE]
```

Team execution goes through the canonical team registry and worker resolver. Catalog-only agents are not executable.

## Current operator surfaces

```text
si web [--host HOST] [--port PORT] [--root PATH] [--allow-remote]
si tui [--root PATH] [--view VIEW] [--filter TEXT] [--once] [--no-color]
```

Web and TUI remain control surfaces over the existing Control API and do not become independent execution authorities.

## v4 target command model

The v4 plan proposes a coherent operator command tree including:

```text
si tasks list|show|pause|resume|stop
si runs list|show
si workflows list|show|run
si models list|test
si agents list|show|run
si teams list|show|run
si opencode status|setup
si omniroute status|models
si logs
si events
si config
```

These commands depend on the v4 runtime, scheduler, OpenCode bridge, OmniRoute integration, and live event/state contracts. They are not claims about the current v3 CLI surface.

## Handoff

```text
si handoff create TEAM --objective TEXT --source termux|codespace --target termux|codespace --output FILE
si handoff inspect FILE [--json]
si handoff import FILE
```

Handoff files are validated portable state. Import does not grant credentials, permissions, tools, harnesses, or execution authority.

## Safety invariants

- Read-only commands do not mutate repository or runtime state.
- Mutating setup/update actions require explicit `--apply`.
- Persona Markdown is data and cannot grant authority.
- OmniRoute remains authoritative for provider/model routing, quota, pricing, fallback, and circuit state.
- Credential-bearing egress remains denied by governance.
- v4 command additions must use the same SI Core/Control API authority rather than implementing a second execution path.