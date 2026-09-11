# SI-Agents v3 — Product & Architecture Roadmap

**Status:** v3 implementation complete  
**Baseline:** SI-Agents v2.0 + Phases 19–43 implemented and CI-verified  
**Remaining:** none in the v3 implementation sequence  
**Primary surfaces:** CLI, SI TUI, localhost Web Control Center  
**Core principle:** one SI Core, one Control API, multiple operator/harness surfaces

## Architecture

SI-Agents is the organization, intelligence, governance, verification, and deployment layer around coding harnesses. It does not replace downstream harnesses or recreate provider routing authority.

```text
                    SI-AGENTS CORE
                          │
                    Control API v1
                          │
             ┌────────────┼────────────┐
             │            │            │
            CLI          TUI          Web
             │            │            │
             └────────────┼────────────┘
                          │
                   Runtime / Governance
                          │
                Harness / Environment
                          │
                       OmniRoute
```

Web and TUI are views/operator boundaries, not authorities. Deployment Center is a governed planning boundary and must not become a second execution authority. Final Integration Hardening is a verification boundary and has no downstream execution authority.

## Phase 42 — Harness Deployment Center

**Complete + CI verified.** Adds immutable harness targets and deployment plans, deterministic validation, fail-closed unknown-target and authority-bearing requests, planning-only manifest preparation, dependency-free Web Deployment Center, `/api/v1/deployments`, and `si deploy`/`si-deploy`. No apply/deploy command or credential migration authority exists.

Implementation merge `70d5f96c15bfbf200804a50f43dc6e12f5dde903`. Final documentation-closed mainline verification was green.

Canonical record: `docs/architecture/PHASE_42_HARNESS_DEPLOYMENT_CENTER.md`.

## Phase 43 — Final v3 Integration & Hardening

**Complete + CI verified.** Adds a deterministic cross-cutting integration audit, immutable integration reports/checks, packaged `si verify`/`si-verify` entry points, canonical catalog/config consistency checks, deployment planning-only hardening, and adversarial release-gate coverage. The audit accepts the repository's canonical schema-versioned governance/organization configuration markers and fails closed for missing or malformed inputs.

Implementation merged as `d4aaddc0008d6af05161d8b79dfc1f9507e0c61e9`. Mainline CI #884 (`34557632059`) exposed a schema-version compatibility regression; PR #50 corrected it and merged as `52588921c0956f091fb569c4b51e9fd741790744`. Final mainline CI #886 (`34558002476`) was green across all repository gates.

Canonical record: `docs/architecture/PHASE_43_INTEGRATION_HARDENING.md`.

## Completion principle

```text
29 Personas [complete]
 → 30 Skills [complete]
 → 31 Rules/Hooks/Events [complete]
 → 32 Memory/Knowledge [complete]
 → 33 Governance [complete]
 → 34 Organization [complete]
 → 35 Control API [complete]
 → 36 Web Foundation [complete]
 → 37 Control Center [complete]
 → 38 Visual Organization/Workflow [complete]
 → 39 Agent Builder [complete]
 → 40 Evidence/Observability [complete]
 → 41 TUI [complete]
 → 42 Harness Deployment [complete]
 → 43 Integration/Hardening [complete]
```

Each phase required implementation, tests, security/adversarial checks, documentation, distribution verification where relevant, and successful CI. That v3 sequence is now closed.

## Post-v3 direction

New work after Phase 43 should be treated as maintenance, security/defect fixes, operational improvements, or explicitly versioned post-v3 features. The v3 roadmap must not silently reopen completed phase contracts.
