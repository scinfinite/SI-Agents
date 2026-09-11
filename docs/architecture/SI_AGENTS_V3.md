# SI-Agents v3 — Product & Architecture Roadmap

**Status:** Active forward roadmap  
**Baseline:** SI-Agents v2.0 + Phases 19–42 implemented and CI-verified  
**Remaining:** Phase 43  
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

Web and TUI are views/operator boundaries, not authorities. Deployment Center is a governed planning boundary and must not become a second execution authority.

## Phase 42 — Harness Deployment Center

**Complete + CI verified.** Adds immutable harness targets and deployment plans, deterministic validation, fail-closed unknown-target and authority-bearing requests, planning-only manifest preparation, dependency-free Web Deployment Center, `/api/v1/deployments`, and `si deploy`/`si-deploy`. No apply/deploy command or credential migration authority exists.

Implementation merge `70d5f96c15bfbf200804a50f43dc6e12f5dde903`. Validation caught and fixed OpenAPI syntax, Ruff, and pytest issues before merge. Final corrected feature validation passed all repository gates.

Canonical record: `docs/architecture/PHASE_42_HARNESS_DEPLOYMENT_CENTER.md`.

## Phase 43 — Final v3 Integration & Hardening

Integrate the complete v3 stack and close remaining architecture, security, verification, distribution, migration/rollback, documentation, and adversarial gaps. Final gates must cover tests, packaging, Ruff, Control API, Web/TUI, organization/catalog consistency, governance/security scanning, evidence integrity, harness conformance, and fail-closed behavior.

## Completion principle

```text
29 Personas [complete]
 → 30 Skills [complete]
 → 31 Rules/Hooks/Events [complete]
 → 32 Memory/Knowledge [complete]
 → 33 Security/Governance [complete]
 → 34 Organization [complete]
 → 35 Control API [complete]
 → 36 Web Foundation [complete]
 → 37 Control Center [complete]
 → 38 Visual Graphs [complete]
 → 39 Agent Builder [complete]
 → 40 Evidence/Observability [complete]
 → 41 TUI [complete]
 → 42 Harness Deployment [complete]
 → 43 Integration/Hardening
```

Each phase requires implementation, tests, security/adversarial checks, documentation, distribution verification where relevant, and successful CI before the next phase begins.
