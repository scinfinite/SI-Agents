# SI-Agents v3 — Product & Architecture Roadmap

**Status:** Active forward roadmap  
**Baseline:** SI-Agents v2.0 + Phases 19–32 implemented and CI-verified; Phase 33 implementation complete pending final CI closure  
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

Phase 29 established the persona-to-typed-contract boundary. Phase 30 established portable Skill artifacts. Phase 31 adds the explicit event/policy layer without creating a parallel permission authority. Phase 32 adds scoped evidence-gated Memory and source-backed Knowledge without turning retrieval into authority. Phase 33 makes governance and security scanning explicit without granting authority to configuration or scanner findings.

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

Canonical architecture record: `docs/architecture/PHASE_29_AGENT_PERSONA.md`.

---

# Phase 30 — First-Class Portable Skills

**State: Complete.** Portable `SKILL.md` artifacts provide deterministic discovery, metadata, validation, versioning, compatibility, composition, provenance, regression coverage, evidence requirements, and safe installation/deployment boundaries.

Canonical architecture record: `docs/architecture/PHASE_30_PORTABLE_SKILLS.md`.

**Invariant:** Skill selection never grants permissions. Skills request capabilities; governance independently authorizes operations.

---

# Phase 31 — Rules, Hooks & Event System

**State: Complete + CI verified.** Explicit Rules, bounded in-process Hooks, immutable Events, fail-closed dangerous-event handling, Skill lifecycle integration, declarative Rule catalog loading, and adversarial regression coverage are implemented. Final CI run **#735** passed the repository audit, Ruff, distribution/wheel verification, and full pytest (**381 passed**) before merge.

Canonical architecture record: `docs/architecture/PHASE_31_RULES_HOOKS_EVENTS.md`.

---

# Phase 32 — Memory & Knowledge

**State: Complete + CI verified.**

Phase 32 delivers durable, provenance-aware memory and source-backed knowledge across:

```text
Task → Project → Team → Agent → Division → Organization → Global
```

Lifecycle:

```text
Observation → Candidate → Evidence → Validation → Promotion → Scoped memory/knowledge
```

Implemented properties:

- immutable scoped MemoryEntry and MemoryEvidence contracts;
- scope identity for task/project/team/agent/division/organization;
- provenance, confidence, lifecycle, expiry, supersession, and contradiction tracking;
- source-backed KnowledgeEntry records requiring verified evidence;
- fail-closed one-scope-at-a-time promotion;
- deterministic context-aware memory and knowledge retrieval;
- atomic schema-versioned JSON persistence with backward-compatible list loading;
- explicit MemoryService lifecycle coordination;
- memory lifecycle EventBus integration;
- security boundary preserving Rules, Hooks, PermissionEngine, and GovernanceEngine authority;
- targeted regression/adversarial coverage.

Feature-branch CI run **#762** passed repository audit, Ruff, distribution/wheel verification, and complete pytest (**392 passed in 5.95s**). Final mainline CI run **#769** passed the same complete gates on merge commit `4662363dbc8e8a401734986d2c92a4be264042ac`, with **392 passed in 5.47s**.

The canonical implementation record is `docs/architecture/PHASE_32_MEMORY_KNOWLEDGE.md`.

---

# Phase 33 — Security & Governance Center

**State: Implementation complete; final mainline CI verification pending.**

Phase 33 makes SI governance a first-class inspectable system and operator-facing core service.

Implemented governance objects include Permission, Capability, Policy, Approval, Risk, Trust Boundary, Credential Reference, Data Classification, Cost Constraint, and typed Governance Request/Decision contracts.

Authorization remains:

```text
Request → Agent/Subject → Skill/Capability → Tool → Environment
        → Policy → Permission → Risk → Approval? → ALLOW / DENY / APPROVAL_REQUIRED
```

Declared capabilities require explicit scoped permissions. Credential-bearing external egress is denied even with approval. Expired approvals cannot authorize. Governance decisions never execute tools or configuration.

`config/governance.v1.json` is validated and packaged as the declarative baseline. `GovernanceScanner` provides deterministic, read-only findings for secret-like literals, broad permissions, unsafe hook commands, suspicious authority-bearing content, and unpinned package execution. Findings carry severity, evidence, remediation guidance, and auto-fixability metadata; scanning never mutates configuration.

Canonical architecture record: `docs/architecture/PHASE_33_SECURITY_GOVERNANCE_CENTER.md`.

---

# Phase 34 — Organization Expansion

Expand the SI organization according to actual responsibilities and verified workflows rather than importing hundreds of external personas.

A mature agent combines:

```text
Markdown Persona + Typed Contract + Skills + Rules
+ Governance + Verification + Memory scope
```

Catalog consistency and source-of-truth validation remain mandatory.

---

# Phase 35 — Control API

Create the stable machine-facing API before the full Web/TUI surfaces. Planned versioned surface includes agents, teams, workflows, Skills, runs, events, evidence, memory, governance, environments, and harnesses. UI mutations go through the API; API mutations go through SI governance; non-local exposure requires explicit authentication/authorization.

---

# Phase 36 — Local Web Foundation

Build a localhost-first Web application launched conceptually by `si web`, with no telemetry by default, strict CORS/CSP, safe static assets, graceful shutdown, safe errors, mutation audit logging, optional authentication for deliberate remote exposure, and no credential leakage into browser payloads.

---

# Phase 37 — SI Control Center

Create the main Web Control Center with Overview, Agents, Teams, Workflows, Skills, Memory, Knowledge, Evidence, Runs, Organization, Governance, Environments, Harnesses, and Settings. It must surface actual live state rather than simulated execution.

---

# Phase 38 — Visual Organization & Workflow

Provide interactive organization and workflow visualization showing divisions, agents, roles, teams, Skills, relationships, capabilities/permissions, and actual execution state.

---

# Phase 39 — Agent Builder & Customization

Allow operators to inspect, customize, create, validate, test, and manage agents through the local Web UI while preserving canonical Markdown and typed contracts. Customization must not become a hidden privilege-escalation path.

---

# Phase 40 — Evidence & Observability

Make the evidence-first architecture visible through inspectable run timelines and evidence detail. Evidence views distinguish facts, observations, inferences, and unresolved uncertainty and expose provenance, confidence, verification state, and supersession/contradiction where applicable.

---

# Phase 41 — SI TUI

Provide a first-class terminal operator interface for Termux, Codespaces, SSH, and other terminal environments. The TUI is an SI organization and operations console, not a replacement for a coding harness.

---

# Phase 42 — Harness Deployment Center

Make SI organization deployment into supported harnesses understandable, inspectable, and governed. Deployment manifests cannot grant permissions, execute workers, migrate credentials, or bypass governance.

---

# Phase 43 — Final v3 Integration & Hardening

Integrate the complete v3 stack and close remaining architecture/security/verification gaps. Final gates cover tests, distribution, Ruff, Control API contracts, Web/TUI checks, organization/catalog consistency, governance/security scanning, evidence integrity, harness conformance, migration/rollback, documentation audit, and adversarial fail-closed checks.

Phase 43 must not be declared complete until final mainline CI evidence is green and current-state documentation matches implementation reality.

---

## v3 completion principle

```text
29 Personas [complete]
 → 30 Skills [complete]
 → 31 Rules/Hooks/Events [complete]
 → 32 Memory/Knowledge [complete]
 → 33 Security/Governance [implementation complete]
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
