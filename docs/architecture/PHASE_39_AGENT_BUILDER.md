# Phase 39 — Agent Builder & Customization

**State:** Complete + CI verified.

## Objective

Provide a local, inspectable authoring surface for creating and customizing SI agent definitions without silently changing the canonical catalog or granting new authority.

## Delivered

- Immutable, bounded `AgentDraft` and `ValidationResult` contracts.
- Deterministic validation against the canonical agent catalog and divisions.
- Editable projections of canonical agents for safe customization.
- New agents cannot self-grant capabilities, permissions, harnesses, or environments.
- Existing customizations cannot add capabilities, permissions, harnesses, or environments and cannot change canonical identity/division.
- Durable local draft store at `.si/agent-builder.json`, written atomically with restrictive file permissions.
- Revision tracking, validation, archive, and non-executing test operations.
- Deterministic Markdown preview explicitly marked as an authoring artifact.
- Dependency-free local Web Agent Builder at `/agent-builder`.
- Versioned Web API/OpenAPI exposure for listing, validating, saving, testing, archiving, and loading canonical-agent projections.
- Builder mutations are audited without logging request bodies or secrets.
- Regression coverage for persistence, authority non-escalation, Web routes, CSP-clean authoring assets, and non-executing validation.

## Authority boundary

The Builder is an authoring and validation layer. It does **not** execute an agent, tool, Skill, workflow, shell command, harness, or external call. It does not mutate `config/agent-catalog.json` and it cannot turn a user-authored field into a new permission boundary. A valid draft is not automatically a canonical or implemented agent.

## Verification

Phase 39 implementation merged from PR #38 as squash commit `22c381e23c6efb2e2eaa1819e975f308fcf3ff73`. Feature CI **#853** (`34511009965`) passed the repository build, wheel installation, repository audit, Ruff, full pytest, diagnostics, and cleanup gates. The final documentation-closed `main` verification is recorded below after the documentation merge.

## Final mainline verification

Pending the final CI run for the documentation-closed mainline tree.

## Next phase

Phase 40 — Evidence & Observability.
