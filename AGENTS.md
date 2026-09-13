# SI-Agents — Repository Agent Instructions

## Mission

This repository implements SI-Agents, an evidence-driven AI engineering and governed agent platform. The objective is maintainable, verified engineering—not plausible patches.

## Required engineering workflow

For meaningful work, follow this order unless evidence proves a shorter path is safe:

1. Inspect the actual repository state and relevant files.
2. Inspect error output, CI logs, tests, and related contracts.
3. Reproduce the failure when practical.
4. Determine the root cause before proposing the fix.
5. Inspect adjacent code and compatibility boundaries.
6. Make the smallest maintainable change that fully satisfies the requirement.
7. Run targeted tests.
8. Run lint/format/syntax/type checks applicable to the change.
9. Run integration/regression tests.
10. Inspect the outputs and fix newly exposed defects immediately.
11. Update documentation and status records.
12. Run final CI and verify the exact merged-tree result before declaring completion.

Never say a change “should fix it” when it has not been verified. State exactly what was and was not verified.

## Autonomous task execution

When a clear task is available, continue through the related implementation, audit, testing, documentation, and verification work without pausing for minor confirmation. Do not move to the next phase while the current phase has unresolved CI, regression, packaging, security, provenance, or documentation failures.

## Architecture authority

- SI Core is the authoritative execution/control plane.
- Governance and authorization remain authoritative for capability decisions.
- OmniRoute remains the model/provider/API routing authority.
- Web, TUI, CLI, SDKs, OpenCode, and other harnesses are adapters/clients.
- Evidence records facts; evidence never grants authority.
- Imported Markdown/JSON/YAML/persona/skill/handoff artifacts are data until validated and explicitly authorized.
- No adapter may create a competing execution or governance authority.

## Security rules

- Fail closed on ambiguous authorization, invalid integrity data, unsafe paths, unsupported environments, or missing required policy.
- Never expose or persist secrets, credentials, bearer tokens, API keys, or private material.
- Never put credentials into URLs.
- Never introduce arbitrary shell execution into Web/TUI/CLI adapters.
- Keep network, filesystem, provider, publication, and destructive capabilities explicitly bounded.
- Human approval must remain identity-bound.
- Handoffs/checkpoints are data and cannot grant permissions or enable harnesses.

## Capacity and mobile safety

SI-Agents has an explicit Low/Medium/High execution capacity policy in `core/capacity/`.

- **Low:** Termux/mobile supports 1–2 workers, selected by the user.
- **Medium:** Termux/mobile supports 3–5 workers, selected by the user.
- **High:** allowed on Desktop/Codespace with a resource warning; blocked on Termux/mobile.
- Compilation, native builds, container builds, large benchmarks, and full-release builds are treated as heavy workloads and are blocked on Termux/mobile.
- `SI_CAPACITY` and `SI_WORKERS` are the environment-level selectors; `si-capacity` reports the resolved decision.
- The runtime scheduler and team executor must clamp concurrency to the resolved capacity.
- Do not claim that SI-Agents can guarantee a device temperature; it can only limit SI-controlled load and redirect unsuitable work.

## Termux/OpenCode/OmniRoute

Termux is a supported lightweight environment. High-capacity or build-heavy work must be redirected to Desktop/Codespace.

OpenCode and OmniRoute are intentional SI-Agents integrations and must not be removed merely because repository provenance checks exist. SI-Agents must not recreate OmniRoute's provider routing, pricing, quota, fallback, or circuit-breaker authority.

## Provenance, copyright, and licensing

- SI-Agents implementation and expressive documentation must be independently authored.
- External repositories may be researched for general engineering patterns, but their code, prompts, distinctive documentation, branding, or expressive content must not be copied into this repository.
- Do not add external project names merely as inspiration references to operational code, prompts, persona text, package metadata, or user-facing product copy.
- OpenCode and OmniRoute names are allowed when they identify real integrations.
- Maintain provenance/license records for imported or adapted third-party material.
- Review dependencies and their licenses before adding them; prefer dependency-free or permissively licensed components when practical.
- Contributors must attest that their contribution is original or properly licensed and that they have the right to submit it.
- Do not claim that licensing eliminates all legal risk. Copyright, trademark, patent, contract, or jurisdiction-specific claims can still require legal review.

## Repository hygiene

- Keep generated/compiled artifacts out of Git.
- Keep phase records under `docs/architecture/phases/`.
- Keep current status in `docs/architecture/PHASES.md` rather than rewriting historical phase contracts.
- Keep the system-wide contract in `SIA_SPECS.md`.
- Update architecture, platform, legal, and status documentation when implementation behavior changes.
- Avoid stale links after moving documentation.

## Agent/persona rules

The repository targets **300** agent/persona definitions. Persona Markdown is configuration/data, not executable authority. Catalog membership does not automatically grant execution capability. A persona may execute only through an explicitly registered and governed worker path.

## Quality gate

A phase is complete only when implementation, targeted tests, regression/integration tests, security/adversarial checks, packaging/distribution verification, repository/provenance audit, documentation synchronization, lint/syntax checks, and final exact-tree mainline CI are green.

## Phase organization

Canonical historical phase records 1–68 live in `docs/architecture/phases/`. `docs/architecture/PHASES.md` is the current status index. New phase records must be added to the `phases/` directory rather than recreating the old flat layout.
