# SI CLI

The `si` command is the operator-facing control surface for SI-Agents. It is a view over the canonical SI Core and typed registries; it is not a second policy authority.

## Read-only diagnostics

```text
si doctor [--json]
si status [--json]
si audit [--json]
```

`si audit` checks required repository structure, catalog loading, persona/catalog parity, hidden Unicode controls, forbidden external branding, temporary Phase 29 artifacts, tracked Python build artifacts, and persona Markdown packaging.

## Discovery

```text
si agents [--division DIVISION] [--status STATUS] [--search TEXT] [--json]
si personas [--division DIVISION] [--search TEXT] [--json]
si teams [--search TEXT] [--json]
```

`agents` reads the authoritative typed catalog. `personas` reads behavioral Markdown through the governed persona registry. These sources are intentionally distinct.

## Setup and updates

```text
si setup [--apply] [--install-opencode] [--configure-opencode] [--model MODEL]
si update [--apply]
```

Setup is dry-run by default. `--apply` is required for mutation. Setup commands are allowlisted; SI does not accept arbitrary shell strings as setup input. OpenCode provider configuration requires an explicit model ID and writes only the local provider configuration.

## Governed execution

```text
si run TEAM --objective TEXT [--handoff FILE]
```

Team execution goes through the canonical team registry and worker resolver. Catalog-only agents are not executable.

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
