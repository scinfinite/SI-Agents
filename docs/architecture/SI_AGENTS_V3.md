# SI-Agents v3 — Product & Architecture Roadmap

**Status:** Active forward roadmap  
**Baseline:** SI-Agents v2.0 + Phases 19–31 implemented; Phases 19–30 CI-verified and Phase 31 awaiting final mainline CI  
**Scope:** Phases 30–43  
**Primary surfaces:** CLI, SI TUI, localhost Web Control Center  
**Core principle:** one SI Core, one Control API, multiple operator/harness surfaces

---

## 1. What SI-Agents v3 is

SI-Agents v3 evolves the verified runtime/governance foundation into a complete, inspectable, customizable **agent organization and control system**.

The v3 layer combines:

- human-authored agent personas
- typed machine contracts
- portable Skills
- scoped Rules, Hooks, and Events
- scoped Memory and Knowledge
- teams and workflows
- Security and Governance
- evidence-first execution and observability
- harness interoperability
- Termux and GitHub Codespaces support
- localhost Web Control Center
- keyboard-first terminal TUI
- a stable Control API shared by operator surfaces

SI-Agents does not replace OpenCode, Codex, Claude Code, Cline, or other harnesses. It is the organization, intelligence, governance, verification, and deployment layer around them.

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

Phase 29 established the persona-to-typed-contract boundary. Phase 30 established portable Skill artifacts. Phase 31 adds the explicit event/policy layer without creating a parallel permission authority.

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

No business logic, authorization logic, agent authority, or workflow engine is duplicated inside Web/TUI surfaces.

### Evidence-first operation

Important operations must remain inspectable: selected agent, selection reason, Skill, requested capabilities/tools, governance decisions, execution events, evidence, verification state, and unresolved uncertainty.

### Security and provenance

Markdown personas, Skills, Rules, Hooks, Memory, deployment manifests, and UI-authored artifacts are data/configuration until explicitly authorized. Importing or editing an artifact must never silently grant permission or execute code. External reference projects inform independently designed implementations under the provenance policy.

### Local-first

The Web Control Center is localhost-first and requires no cloud control plane or telemetry service by default. Remote exposure, credentials, network access, paid resources, publication, destructive operations, and sensitive data require explicit governance.

---

# Phase 29 — Agent Persona & Definition System

**State: Complete.** Deterministic Markdown personas, typed behavioral contracts, validation, governed compilation, duplicate/conflict detection, canonical personas, provenance, inert-content handling, and distribution packaging are implemented and CI-verified.

---

# Phase 30 — First-Class Portable Skills

**State: Complete.**

Portable `SKILL.md` artifacts provide deterministic discovery, metadata, validation, versioning, compatibility, composition, provenance, regression coverage, evidence requirements, and safe installation/deployment boundaries.

A Skill defines identity/version, purpose, inputs/outputs, prerequisites, workflow, tools, capabilities, permissions, verification, failure behavior, evidence, examples, compatibility, and provenance.

**Invariant:** Skill selection never grants permissions. Skills request capabilities; governance independently authorizes operations.

---

# Phase 31 — Rules, Hooks & Event System

**State: Implementation complete; final mainline CI pending.**

Phase 31 adds an explicit policy/event layer spanning agents, Skills, tools, workflows, runtime, handoffs, and verification.

Implemented properties:

- explicit Rule and Hook registration;
- immutable bounded Event envelopes;
- canonical lifecycle event vocabulary;
- deterministic exact-match Rule evaluation;
- declarative Rule catalog loading with no code execution;
- bounded in-process Hooks with observer/gate separation;
- per-event hook limits and runtime budgets;
- fail-closed handling for dangerous events and gate-hook failures;
- secret-like event payload redaction;
- Skill lifecycle/verification event integration;
- separation from existing PermissionEngine/GovernanceEngine authority;
- regression/adversarial coverage and package inclusion.

Rules and Hooks never grant permissions, credentials, tools, network access, or execution authority. No arbitrary shell/command hook registration is supported.

The canonical implementation record is `docs/architecture/PHASE_31.md` and the canonical declarative Rule catalog is `config/rules.v1.json`.

---

# Phase 32 — Memory & Knowledge

Build durable, provenance-aware memory/knowledge across:

```text
Global → Organization → Division → Agent → Team → Project → Task → Evidence
```

Lifecycle:

```text
Observation → Candidate → Evidence → Validation → Promotion → Scoped memory/knowledge
```

Track source, scope, timestamps, confidence, provenance, evidence references, version, supersession, expiration, and validation state. Retrieval is not proof; promotion remains evidence-gated and fail-closed.

---

# Phase 33 — Security & Governance Center

Expose SI governance as a first-class inspectable system and operator experience.

Governance objects include Permission, Capability, Policy, Approval, Risk, Trust Boundary, Credential Reference, Data Classification, Network Access, and Cost Constraint.

Authorization remains conceptually:

```text
Request → Agent → Skill → Tool → Environment → Policy
        → Permission → Risk → Approval? → ALLOW / DENY
```

Add a scanner for agent definitions, Skills, Rules, Hooks, permissions, capabilities, harness/environment configuration, secret-like content, unsafe execution paths, privilege escalation risks, and suspicious configuration. Findings include severity, evidence, and remediation guidance; scanning never silently modifies configuration.

---

# Phase 34 — Organization Expansion

Expand the SI organization according to actual responsibilities and verified workflows rather than importing hundreds of external personas.

Potential SI-native divisions include Engineering, Architecture, Debugging, Testing, Security, Research, Product, Design, Data, DevOps, Infrastructure, Operations, Documentation, Quality, Project Management, Finance, Legal/Compliance, Support, AI/ML, Mobile, Web, Cloud, Database, and Performance.

A mature agent combines:

```text
Markdown Persona + Typed Contract + Skills + Rules
+ Governance + Verification + Memory scope
```

Catalog consistency and source-of-truth validation remain mandatory.

---

# Phase 35 — Control API

Create the stable machine-facing API before the full Web/TUI surfaces.

Planned versioned surface includes agents, teams, workflows, Skills, runs, events, evidence, memory, governance, environments, and harnesses. Exact endpoints may evolve during implementation but must remain typed and versioned.

Rules:

- UI mutations go through the API.
- API mutations go through SI governance.
- Web/TUI never treat internal Python classes as authority.
- Responses are typed and deterministic.
- Non-local exposure requires explicit authentication/authorization.

---

# Phase 36 — Local Web Foundation

Build a localhost-first Web application launched conceptually by `si web`.

Requirements: no telemetry by default, no mandatory cloud service, strict CORS/CSP, safe static assets, graceful shutdown, safe errors, mutation audit logging, optional authentication for deliberate remote exposure, and no credential leakage into browser payloads.

The Web application is an operator surface, not a second runtime.

---

# Phase 37 — SI Control Center

Create the main Web Control Center with Overview, Agents, Teams, Workflows, Skills, Memory, Knowledge, Evidence, Runs, Organization, Governance, Environments, Harnesses, and Settings.

The dashboard should surface live state such as active runs, available agents, Skills, events, verification state, governance findings, environment readiness, recent evidence, and failed/degraded executions.

---

# Phase 38 — Visual Organization & Workflow

Provide interactive organization and workflow visualization showing divisions, agents, roles, teams, Skills, relationships, capabilities/permissions, and execution state.

Workflow visualization must reflect actual runtime events, for example:

```text
queued → running → waiting → verified → completed
                         ↘ failed / escalated
```

Support search, filtering, zooming, panning, and drill-down without inventing simulated execution state.

---

# Phase 39 — Agent Builder & Customization

Allow operators to inspect, customize, create, validate, test, and manage agents through the local Web UI while preserving canonical Markdown and typed contracts.

The builder covers identity, mission, personality, expertise, Skills, tools, capabilities, permissions, workflow, Rules, memory, verification, security, testing, and publication.

A controlled dry-run/test path must evaluate persona validity, Skill compatibility, governance compatibility, expected behavior, verification, and security findings. Customization must not become a hidden privilege-escalation path.

---

# Phase 40 — Evidence & Observability

Make the evidence-first architecture visible through inspectable run timelines and evidence detail.

A run should expose major events from task start through agent/Skill selection, inspection, diagnosis, actions, governance, tests, verification, and completion/failure/escalation.

Evidence views should distinguish facts, observations, inferences, and unresolved uncertainty and expose evidence ID, source, timestamp, provenance, supported claim, confidence, verification state, related run/task/agent, and supersession/contradiction where applicable.

---

# Phase 41 — SI TUI

Provide a first-class terminal operator interface for Termux, Codespaces, SSH, and other terminal environments.

The SI TUI is **not an OpenCode clone**. OpenCode remains a coding/agent harness; the TUI is the SI organization and operations console.

Requirements: keyboard-first operation, low resource usage, accessible textual state, live execution events, agent/team/run inspection, governance/evidence inspection, and the same Control API as Web.

---

# Phase 42 — Harness Deployment Center

Make SI organization deployment into supported harnesses understandable, inspectable, and governed.

Initial targets include OpenCode, Codex, Claude Code, Cline, Antigravity, and a Universal SI protocol.

Deployment remains descriptive until explicit runtime registration/governance enables a harness. Deployment manifests cannot grant permissions, execute workers, migrate credentials, or bypass governance.

---

# Phase 43 — Final v3 Integration & Hardening

Integrate the complete v3 stack and close remaining architecture/security/verification gaps.

Final gates should cover:

- complete unit/integration/system/regression tests;
- distribution and installation verification;
- Ruff/lint and static validation;
- Control API contract checks;
- Web/TUI surface checks;
- organization/catalog/persona/Skill consistency;
- governance and security scanning;
- evidence/observability integrity;
- harness deployment conformance;
- migration/rollback review;
- documentation/source-of-truth audit;
- adversarial and fail-closed regression checks.

Phase 43 must not be declared complete until the final mainline CI evidence is green and the repository's current-state documentation matches implementation reality.

---

## v3 completion principle

The v3 program is layered and must be completed in order:

```text
29 Personas [complete]
 → 30 Skills [complete]
 → 31 Rules/Hooks/Events [implementation complete; CI pending]
 → 32 Memory/Knowledge
 → 33 Security/Governance
 → 34 Organization
 → 35 Control API
 → 36 Web Foundation
 → 37 Control Center
 → 38 Visual Graphs
 → 39 Agent Builder
 → 40 Evidence/Observability
 → 41 TUI
 → 42 Harness Deployment
 → 43 Integration/Hardening
```

Each phase requires implementation, tests, security/adversarial checks, documentation, distribution verification where relevant, and successful CI before the next phase begins.
