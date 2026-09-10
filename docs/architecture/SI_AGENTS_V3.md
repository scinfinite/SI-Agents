# SI-Agents v3 — Product & Architecture Roadmap

**Status:** Active forward roadmap  
**Baseline:** SI-Agents v2.0 + Phases 19–38 implemented and CI-verified  
**Scope:** Phases 30–43  
**Primary surfaces:** CLI, SI TUI, localhost Web Control Center  
**Core principle:** one SI Core, one Control API, multiple operator/harness surfaces

---

## 1. What SI-Agents v3 is

SI-Agents v3 evolves the verified runtime/governance foundation into a complete, inspectable, customizable **agent organization and control system**.

The v3 layer combines human-authored agent personas, typed machine contracts, portable Skills, scoped Rules/Hooks/Events, scoped Memory/Knowledge, teams/workflows, Security/Governance, evidence-first execution/observability, harness interoperability, Termux/Codespaces support, localhost Web Control Center, keyboard-first TUI, and a stable Control API shared by operator surfaces.

SI-Agents does not replace coding harnesses. It is the organization, intelligence, governance, verification, and deployment layer around them.

**OmniRoute remains the model/provider routing authority.** SI-Agents must not recreate provider quota, pricing, fallback, circuit-breaker, or model-routing authority around OmniRoute.

## 2. Architectural principles

### One source of truth

```text
Human-authored Markdown Persona
            ↓
       Persona Parser
            ↓
   Typed Agent Definition
            ↓
 Organization / Registry
            ↓
 Skills + Rules + Governance
            ↓
        SI Runtime
            ↓
   Control API / Execution
```

Phase 29 established the persona-to-typed-contract boundary. Phase 30 established portable Skill artifacts. Phase 31 added the explicit event/policy layer without creating a parallel permission authority. Phase 32 added scoped evidence-gated Memory and source-backed Knowledge without turning retrieval into authority. Phase 33 made governance and security scanning explicit without granting authority to configuration or scanner findings. Phase 34 added a declarative organization layer that coordinates existing agents into operating teams and verified workflows without becoming a new authority boundary. Phase 35 established the stable machine-facing API over those existing authorities. Phase 36 established the first Web transport/presentation boundary over that API. Phase 37 turned that foundation into the live Control Center. Phase 38 adds visual organization/workflow inspection while preserving the same authority boundary.

### Web and TUI are views, not authorities

```text
                    SI-AGENTS CORE
                          │
                    Control API
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

No business logic, authorization logic, agent authority, or workflow engine is duplicated inside Web/TUI surfaces. Phase 38 graph rendering is a read-only projection and must remain so.

### Evidence-first operation

Important operations must remain inspectable: selected agent, selection reason, Skill, requested capabilities/tools, governance decisions, execution events, evidence, verification state, and unresolved uncertainty.

### Security and provenance

Markdown personas, Skills, Rules, Hooks, Memory, deployment manifests, and UI-authored artifacts are data/configuration until explicitly authorized. Importing or editing an artifact must never silently grant permission or execute code. Public implementation claims must match independently verified SI-owned behavior and current repository evidence.

### Local-first

The Web Control Center is localhost-first and requires no cloud control plane or telemetry service by default. Remote exposure, credentials, network access, paid resources, publication, destructive operations, and sensitive data require explicit governance.

---

# Phase 38 — Visual Organization & Workflow

**State: Complete + CI verified.**

Phase 38 provides a deterministic visual read model and dependency-free SVG operator surface for organizational and workflow topology. It covers divisions, teams, agents, Skills, capabilities, permissions, workflows, steps, dependencies, relationships, and current control-plane run state. Organization, workflow, and Skills/security graph modes support filtering, node inspection, pan/zoom/reset, responsive layout, and keyboard activation.

The visualization remains read-only: it does not edit artifacts, authorize requests, execute workers/tools/workflows, or infer downstream execution progress. `/api/v1/visualization` and the Control Center aggregate expose the same canonical state used elsewhere by the operator UI.

Final mainline CI **#845** (`34508914827`) passed all repository gates on implementation merge commit `657530eefa41794fb425cd0fe38d2aced9bd316d`.

Canonical record: `docs/architecture/PHASE_38_VISUAL_ORGANIZATION_WORKFLOW.md`.

---

# Phase 39 — Agent Builder & Customization

Allow operators to inspect, customize, create, validate, test, and manage agents through the local Web UI while preserving canonical Markdown and typed contracts. Customization must not become a hidden privilege-escalation path.

# Phase 40 — Evidence & Observability

Make the evidence-first architecture visible through inspectable run timelines and evidence detail. Evidence views distinguish facts, observations, inferences, and unresolved uncertainty and expose provenance, confidence, verification state, and supersession/contradiction where applicable.

# Phase 41 — SI TUI

Provide a first-class terminal operator interface for Termux, Codespaces, SSH, and other terminal environments. The TUI is an SI organization and operations console, not a replacement for a coding harness.

# Phase 42 — Harness Deployment Center

Make SI organization deployment into supported harnesses understandable, inspectable, and governed. Deployment manifests cannot grant permissions, execute workers, migrate credentials, or bypass governance.

# Phase 43 — Final v3 Integration & Hardening

Integrate the complete v3 stack and close remaining architecture/security/verification gaps. Final gates cover tests, distribution, Ruff, Control API contracts, Web/TUI checks, organization/catalog consistency, governance/security scanning, evidence integrity, harness conformance, migration/rollback, documentation audit, and adversarial fail-closed checks.

Phase 43 must not be declared complete until final mainline CI evidence is green and current-state documentation matches implementation reality.

## v3 completion principle

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
 → 39 Agent Builder
 → 40 Evidence/Observability
 → 41 TUI
 → 42 Harness Deployment
 → 43 Integration/Hardening
```

Each phase requires implementation, tests, security/adversarial checks, documentation, distribution verification where relevant, and successful CI before the next phase begins.
