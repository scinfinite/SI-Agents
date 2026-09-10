# Phase 33 — Security & Governance Center

**Status:** Complete + CI verified.

## Scope

Phase 33 makes security and governance a first-class, inspectable SI Core boundary. Governance remains an authorization authority; Memory/Knowledge, Skills, Rules, Hooks, and operator surfaces cannot silently grant permission.

## Governance objects

`core/governance/models.py` defines typed contracts for Permission, Capability, Policy, Approval, Risk, Trust Boundary, Credential Reference, Data Classification, Cost Constraint, and Governance Request/Decision.

## Authorization boundary

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

`GovernanceScanner` performs a read-only deterministic repository scan. It reports secret-like literals, broad/wildcard permissions, unsafe hook/command patterns, prompt-injection-like authority instructions, and unpinned package execution in configuration.

Each finding contains a stable rule ID, severity, path, evidence, remediation guidance, and auto-fixability flag. The scanner never modifies the repository and does not silently fix findings.

## Verification evidence

Phase 33 feature CI run **#785** passed build/distribution verification, wheel installation, repository audit, Ruff, and the full pytest suite (**402 passed**). The implementation was merged to `main` as commit `765782377def8173ea235f1bbb3f8c3f9c194767`.

Mainline CI run **#786** passed all build, wheel, repository-audit, Ruff, and pytest steps on that exact merge commit.

## External pattern review

Current public engineering references were reviewed for least privilege, configuration scanning, secret detection, hook/MCP risk analysis, explicit security scope, evidence-backed remediation, and CI-friendly structured reports. SI-Agents generalizes those engineering patterns into its dependency-free Python governance boundary rather than copying external code, prompts, branding, or implementation structure.

## Exit gate

All Phase 33 exit gates are satisfied: implementation, adversarial regression coverage, repository audit, Ruff, distribution/wheel verification, full pytest, synchronized documentation, merge to `main`, and final green mainline CI.
