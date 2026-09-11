# SI-Agents v3 — Product & Architecture Roadmap

**Status:** Active forward roadmap  
**Baseline:** SI-Agents v2.0 + Phases 19–41 implemented and CI-verified  
**Remaining:** Phases 42–43  
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

Web and TUI are views/operator boundaries, not authorities. They must not duplicate authorization, workflow execution, agent authority, credential storage, or provider-routing logic.

### Evidence-first operation

Important operations remain inspectable through explicit evidence: provenance, source, confidence, verification state, supersession/contradiction, unresolved uncertainty, control-plane events, and run relationships. Recording evidence does not make a claim automatically true or verified.

### Security and provenance

Personas, Skills, Rules, Hooks, Memory, deployment manifests, Builder drafts, evidence, and UI state are data/configuration until explicitly authorized. Importing or editing artifacts must never silently grant permission or execute code. Remote exposure, credentials, network access, paid resources, publication, destructive actions, and sensitive data require explicit governance.

## Phase 38 — Visual Organization & Workflow

**Complete + CI verified.** Deterministic graph read model and dependency-free SVG operator surface for organizational/workflow topology with filtering, inspection, pan/zoom/reset, keyboard access, and explicit read-only execution boundaries. Final mainline CI #845 (`34508914827`) was green.

## Phase 39 — Agent Builder & Customization

**Complete + CI verified.** Governed local authoring surface with immutable bounded drafts, canonical projections, non-escalation validation, atomic persistence, revision/archive/test lifecycle, deterministic Markdown previews, Web/API/OpenAPI integration, and no execution authority. Implementation merge `22c381e23c6efb2e2eaa1819e975f308fcf3ff73`; final mainline CI #857 (`34511559646`) was green.

## Phase 40 — Evidence & Observability

**Complete + CI verified.** Typed evidence records for facts, observations, inferences, and uncertainties; bounded confidence; explicit verification; provenance; run relationships; contradiction/supersession; atomic restrictive persistence; Control API evidence routes/timelines; Evidence Explorer; and regression coverage. Final mainline CI #864 (`34513486696`) was green with 458 tests passed.

## Phase 41 — SI TUI

**Complete + CI verified.** Dependency-free keyboard-first terminal operator interface for Termux, Codespaces, SSH, and ordinary terminals. It consumes the same `ControlApiService` as Web and covers Overview, Agents, Teams, Workflows, Skills, Memory, Knowledge, Evidence, Runs, Organization, Governance, Environments, Harnesses, and Settings. Navigation, filtering, selection, refresh, and terminal rendering are local UI behavior; there is no mutation or execution authority. `--once`, `--filter`, `--view`, `--no-color`, and `NO_COLOR` support deterministic/non-interactive use.

Implementation merge `531d2b964a6567aaa0a6b34b2d9b8f4471eb83f5`; feature CI #865 (`34553393908`) and post-merge mainline CI #866 (`34553461275`) were green.

Canonical record: `docs/architecture/PHASE_41_TUI.md`.

## Phase 42 — Harness Deployment Center

Make SI organization deployment into supported harnesses understandable, inspectable, and governed. Deployment manifests cannot grant permissions, execute workers, migrate credentials, or bypass governance.

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
 → 42 Harness Deployment
 → 43 Integration/Hardening
```

Each phase requires implementation, tests, security/adversarial checks, documentation, distribution verification where relevant, and successful CI before the next phase begins.
