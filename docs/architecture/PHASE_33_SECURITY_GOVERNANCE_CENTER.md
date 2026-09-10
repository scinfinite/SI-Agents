# Phase 33 — Security & Governance Center

**Status:** Implementation complete; awaiting final mainline CI verification.

## Scope

Phase 33 makes security and governance a first-class, inspectable SI Core boundary. Governance remains an authorization authority; Memory/Knowledge, Skills, Rules, Hooks, and operator surfaces cannot silently grant permission.

## Governance objects

`core/governance/models.py` defines typed contracts for:

- Permission
- Capability
- Policy
- Approval
- Risk
- Trust Boundary
- Credential Reference
- Data Classification
- Cost Constraint
- Governance Request / Decision

All security-sensitive objects validate required scope, identity, risk, and lifecycle information at construction time.

## Authorization boundary

The decision flow is:

```text
Request → Agent/Subject → Skill/Capability → Tool → Environment
        → Policy → Permission → Risk → Approval? → ALLOW / DENY / APPROVAL_REQUIRED
```

The `GovernanceEngine` is fail-closed for declared capabilities: a request that names a subject and capability must have an explicit scoped allow permission. Credential-bearing external egress is denied even when an approval is supplied. Expired approvals do not authorize operations.

Governance does not execute tools, commands, credentials, network requests, or configuration. It returns a typed decision with reasons and effective risk.

## Declarative catalog

`config/governance.v1.json` provides a dependency-free baseline capability/policy catalog. `core/governance/catalog.py` validates schema version and typed enum values before loading it into `GovernanceStore`.

The catalog is packaged with distributions so installed SI environments retain the same governance baseline.

## Audit

The existing `AuditLog` remains intentionally summary-only: it records action, decision, effective risk, reasons, and timestamp without copying approvals or sensitive request payloads.

## Security scanner

`GovernanceScanner` performs a read-only deterministic repository scan. It reports:

- secret-like literals;
- broad/wildcard permissions;
- unsafe hook/command patterns;
- prompt-injection-like authority instructions;
- unpinned package execution in configuration.

Each finding contains a stable rule ID, severity, path, evidence, remediation guidance, and auto-fixability flag. The scanner never modifies the repository and does not silently fix findings.

The scanner intentionally avoids treating ordinary documentation URLs as security findings; security checks are grounded in executable/configuration patterns rather than generic prose.

## Adversarial guarantees

Coverage includes:

- missing scoped permissions;
- invalid permission and trust-boundary definitions;
- expired approvals;
- credential + external-egress denial even with approval;
- policy denial that cannot be overridden by approval;
- malformed governance catalogs;
- secret, wildcard permission, unsafe hook, injection, and unpinned-tool scanner findings;
- scanner determinism and read-only behavior.

## External pattern review

Current external references were reviewed for security scanning, least-privilege configuration, evidence-backed remediation, and fail-closed security workflows. ECC's current AgentShield model emphasizes scanning secrets, permissions, hooks, MCP/configuration, and agent definitions with CI-friendly structured output; Agency Agents emphasizes explicit security scope, no credentials in Markdown agent definitions, and evidence-backed remediation. citeturn1search0turn1search1turn1search7turn0search0turn0search2

SI-Agents generalizes these patterns into its dependency-free Python governance boundary rather than copying external code, prompts, or implementation structure.

## Exit gate

Phase 33 is complete only after:

1. feature tests pass;
2. repository audit passes;
3. Ruff passes;
4. distribution and wheel installation checks pass;
5. full pytest passes;
6. documentation is synchronized;
7. the merged `main` commit receives a final green CI run.
