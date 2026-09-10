# SI-Agents v3 — Product & Architecture Roadmap

**Status:** Planned roadmap  
**Baseline:** SI-Agents v2.0 + Phases 19–28 complete/CI-verified  
**Scope:** Phases 29–43  
**Primary surfaces:** CLI, SI TUI, localhost Web Control Center  
**Core principle:** one SI Core, one Control API, multiple operator/harness surfaces

---

## 1. What SI-Agents v3 is

SI-Agents v3 is the next major evolution of SI-Agents from a strong agent-runtime and governance foundation into a complete, inspectable, customizable **agent organization and control system**.

v3 will combine:

- rich human-authored agent personas
- machine-readable typed agent contracts
- reusable skills
- rules and event hooks
- scoped memory and knowledge
- teams and workflows
- security and governance
- evidence-first execution and observability
- harness interoperability
- Termux and GitHub Codespaces support
- a polished localhost Web Control Center
- a keyboard-first terminal TUI
- a stable Control API shared by all operator surfaces

The goal is not to replace OpenCode, Codex, Claude Code, or other agent harnesses. SI-Agents is the **organization, intelligence, governance, verification, and deployment layer** around them.

OmniRoute remains the **model/provider routing authority**. SI-Agents must not recreate OmniRoute's provider quota, pricing, fallback, circuit-breaker, or model-routing responsibilities.

---

## 2. v3 architectural principles

### 2.1 One source of truth

Agent organization metadata must not drift between catalogs, UI lists, adapters, and documentation.

The intended model is:

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

Markdown is the rich behavioral authoring layer. Typed contracts remain the machine-enforced layer.

### 2.2 Web and TUI are views, not authorities

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

No business logic, authorization logic, agent model, or workflow engine is duplicated inside the Web UI or TUI.

### 2.3 Evidence-first operation

Every important v3 operation should remain inspectable and verifiable. The system should be able to answer:

- Which agent was selected?
- Why was it selected?
- Which skill was used?
- Which tools/capabilities were requested?
- Which policies allowed or denied the action?
- What happened during execution?
- What evidence supports the result?
- What was verified and what remains uncertain?

### 2.4 Security is part of the architecture

Agent Markdown, skills, hooks, memory, deployment manifests, and UI mutations are data/configuration until explicitly authorized by the appropriate runtime and governance layer. Importing or editing an artifact must never silently grant permission or execute code.

### 2.5 Local-first

The Web Control Center is localhost-first. v3 should work without requiring a cloud control plane or telemetry service. Remote exposure, credentials, network access, and other high-risk operations require explicit governance.

---

# Phase 29 — Agent Persona & Definition System

## Objective

Introduce rich, human-authored agent definitions inspired by the useful pattern used by Agency Agents while retaining SI-Agents' typed contracts, governance, lifecycle, capability, and verification model.

## Planned structure

```text
agents/
├── engineering/
│   ├── developer.md
│   ├── backend-engineer.md
│   └── infrastructure-engineer.md
├── debugging/
│   └── debugger.md
├── verification/
│   ├── tester.md
│   └── code-reviewer.md
└── security/
    └── security-engineer.md
```

## Persona contents

A persona should support frontmatter and structured sections such as:

- name
- description
- identity
- personality/vibe
- core mission
- expertise
- responsibilities
- workflow
- critical rules
- boundaries
- deliverables
- failure behavior
- escalation behavior
- verification expectations
- evidence requirements

## Typed integration

The Markdown persona must not replace `AgentDefinition`. Instead:

```text
agent.md
   ↓ parse + validate
AgentPersona
   ↓ compile/merge
AgentDefinition
   ↓ governance validation
Executable/declarative agent registration
```

The typed contract remains authoritative for machine-enforced properties such as capabilities, permissions, lifecycle, harness compatibility, environment compatibility, and execution status.

## Acceptance criteria

- deterministic Markdown parsing
- frontmatter/schema validation
- required-section validation
- stable agent identity
- duplicate/conflict detection
- versioning and migration support
- canonical source-of-truth rules
- persona-to-contract tests
- safe handling of malformed or malicious persona content
- UI-readable metadata

---

# Phase 30 — Skills & Intelligence

## Objective

Turn skills into first-class portable SI artifacts rather than implicit procedures embedded inside agents.

## Planned structure

```text
skills/
└── engineering/
    └── root-cause-analysis/
        └── SKILL.md
```

## Skill metadata

A skill should define:

- identity/version
- purpose
- inputs
- outputs
- prerequisites
- workflow/procedure
- required tools
- required capabilities
- required permissions
- verification requirements
- failure conditions
- evidence requirements
- examples
- compatibility
- provenance

## Core rule

**Skill selection never grants permissions.**

A skill may request capabilities, but governance must independently authorize the resulting operation.

## Planned capabilities

- discovery/search
- deterministic loading
- validation
- versioning
- compatibility checks
- skill composition
- provenance tracking
- regression tests
- evidence requirements
- safe installation/deployment boundaries

---

# Phase 31 — Rules, Hooks & Event System

## Objective

Create a controlled policy/event layer for predictable behavior across agents, skills, tools, workflows, and runtime execution.

## Rules

Rules should express constraints and behavioral requirements independently of individual personas.

Examples:

- security rules
- repository rules
- testing rules
- cost rules
- evidence rules
- environment rules
- project-specific rules

## Events

The event model should cover events such as:

```text
session.created
session.closed
task.started
agent.selected
skill.started
skill.completed
tool.before
tool.after
handoff.created
verification.started
verification.failed
task.completed
task.failed
```

## Hooks

Hooks should be:

- registered explicitly
- bounded
- auditable
- policy-aware
- deterministic where practical
- fail-closed for dangerous operations
- unable to silently bypass governance

Hook execution must not become an unrestricted arbitrary-command system.

---

# Phase 32 — Memory & Knowledge

## Objective

Build a durable, provenance-aware memory and knowledge system that supports agents and teams without turning unverified observations into authoritative knowledge.

## Scope hierarchy

```text
Global
  ↓
Organization
  ↓
Division
  ↓
Agent
  ↓
Team
  ↓
Project
  ↓
Task
  ↓
Evidence
```

## Memory lifecycle

```text
Observation
   ↓
Candidate
   ↓
Evidence
   ↓
Validation
   ↓
Promotion
   ↓
Scoped memory/knowledge
```

## Memory metadata

Memory should track:

- source
- scope
- creation/update time
- confidence
- provenance
- evidence references
- version
- supersedes relationship
- expiration where applicable
- validation state

The system should support search, retrieval, supersession, lifecycle management, and auditability.

---

# Phase 33 — Security & Governance Center

## Objective

Expose SI-Agents' existing governance philosophy as a first-class system and operator experience.

## Governance objects

- Permission
- Capability
- Policy
- Approval
- Risk
- Trust boundary
- Credential reference
- Data classification
- Network access
- Cost constraint

## Authorization pipeline

```text
Request
  ↓
Agent
  ↓
Skill
  ↓
Tool
  ↓
Environment
  ↓
Policy
  ↓
Permission
  ↓
Risk
  ↓
Approval?
  ↓
ALLOW / DENY
```

## Security scanner

Add a security/configuration scanner for:

- agent definitions
- skills
- rules
- hooks
- permissions
- capabilities
- harness configuration
- environment configuration
- secret-like content
- unsafe execution paths
- privilege escalation risks
- suspicious configuration

The scanner should provide findings, severity, evidence, and remediation guidance rather than silently modifying configuration.

---

# Phase 34 — Organization Expansion

## Objective

Expand the SI organization into a useful, coherent set of specialized agents without blindly importing hundreds of external personas.

## Initial SI-native divisions

Potential divisions include:

- Engineering
- Architecture
- Debugging
- Testing
- Security
- Research
- Product
- Design
- Data
- DevOps
- Infrastructure
- Operations
- Documentation
- Quality
- Project Management
- Finance
- Legal/Compliance
- Support
- AI/ML
- Mobile
- Web
- Cloud
- Database
- Performance

The final catalog must be driven by actual SI responsibilities and verified workflows.

## Agent composition

Each mature agent should combine:

```text
Markdown Persona
+ Typed Contract
+ Skills
+ Rules
+ Governance
+ Verification
+ Memory scope
```

Catalog consistency and source-of-truth validation remain mandatory.

---

# Phase 35 — Agent Runtime API / Control API

## Objective

Create a stable machine-facing Control API before building the full Web and TUI surfaces.

## Planned API surface

```text
GET    /api/v1/agents
POST   /api/v1/agents
PUT    /api/v1/agents/:id
DELETE /api/v1/agents/:id

GET    /api/v1/teams
GET    /api/v1/workflows
GET    /api/v1/skills

POST   /api/v1/runs
GET    /api/v1/runs/:id
POST   /api/v1/runs/:id/cancel

GET    /api/v1/events
GET    /api/v1/evidence
GET    /api/v1/memory
GET    /api/v1/governance
GET    /api/v1/environments
GET    /api/v1/harnesses
```

Exact endpoints may evolve during implementation, but the contract must be versioned and stable.

## Rules

- UI mutations go through the API.
- API mutations go through SI governance.
- Web/TUI never import internal Python implementation classes as their authority.
- API responses are typed and deterministic.
- Authentication/authorization requirements are explicit for any non-local exposure.

---

# Phase 36 — Local Web App Foundation

## Objective

Build a polished localhost Web application similar in spirit to a local control dashboard such as OmniRoute's local interface, but purpose-built for SI-Agents.

## CLI entry point

The intended experience is conceptually:

```text
si web
```

which starts the local server and reports a localhost address such as:

```text
http://127.0.0.1:<port>
```

## Requirements

- localhost-first
- no telemetry by default
- no mandatory cloud service
- strict CORS
- appropriate CSP
- safe static asset serving
- graceful shutdown
- safe error handling
- audit logging for mutations
- optional authentication if deliberately exposed beyond localhost
- no credential leakage into browser payloads

The Web application is an operator surface, not a second runtime.

---

# Phase 37 — SI Control Center

## Objective

Create the main Web Control Center for understanding and operating the SI organization.

## Main areas

- Overview
- Agents
- Teams
- Workflows
- Skills
- Memory
- Knowledge
- Evidence
- Runs
- Organization
- Governance
- Environments
- Harnesses
- Settings

## Dashboard

The overview should surface useful live state such as:

- active runs
- available agents
- teams
- skills
- recent events
- verification status
- governance findings
- environment readiness
- recent evidence
- failed/degraded executions

The design should prioritize excellent visual hierarchy, responsive interaction, clear state, useful animations, and accessibility without making animation interfere with operation.

---

# Phase 38 — Visual Organization & Workflow

## Objective

Make the agent organization and execution workflows visually understandable.

## Organization visualization

Provide an interactive graph/tree capable of showing:

- divisions
- agents
- roles
- teams
- skills
- relationships
- permissions/capabilities
- execution state

Support search, filtering, zooming, panning, and drill-down.

## Workflow visualization

Provide a live workflow graph showing:

```text
queued → running → waiting → verified → completed
                         ↘ failed/escalated
```

Execution animation should reflect actual runtime events rather than simulated state.

---

# Phase 39 — Agent Builder & Customization

## Objective

Allow users to inspect, customize, create, validate, test, and manage agents through the local Web UI.

## Agent Builder stages

```text
Identity
  ↓
Mission
  ↓
Personality
  ↓
Expertise
  ↓
Skills
  ↓
Tools
  ↓
Capabilities
  ↓
Permissions
  ↓
Workflow
  ↓
Rules
  ↓
Memory
  ↓
Verification
  ↓
Security
  ↓
Test
  ↓
Publish
```

## Source-of-truth behavior

The UI should edit the canonical Markdown persona and corresponding validated machine contract rather than creating an opaque UI-only agent definition.

## Testing

Provide a controlled dry-run/test experience that can evaluate:

- persona validity
- skill compatibility
- governance compatibility
- expected behavior
- verification requirements
- security findings

A user must not be able to use customization as a hidden permission-escalation path.

---

# Phase 40 — Evidence & Observability

## Objective

Make SI-Agents' evidence-first architecture visible and useful to operators.

## Run timeline

A run should be inspectable as a sequence similar to:

```text
Task started
  ↓
Agent selected
  ↓
Skill selected
  ↓
Repository/context inspected
  ↓
Problem reproduced
  ↓
Hypothesis/root cause
  ↓
Change/action
  ↓
Governance checks
  ↓
Tests
  ↓
Reality check
  ↓
Verification
  ↓
Completed / Failed / Escalated
```

Each important event should link to supporting evidence where available.

## Evidence UI

Operators should be able to inspect:

- evidence ID
- source
- timestamp
- provenance
- claim supported
- confidence
- verification state
- related run/task/agent
- supersession/contradiction where applicable

The UI must clearly distinguish facts, observations, inferences, and unresolved uncertainty.

---

# Phase 41 — SI TUI

## Objective

Provide a first-class terminal operator interface for Termux, Codespaces, SSH, and other terminal environments.

## Positioning

The SI TUI is **not an OpenCode clone**.

OpenCode remains the coding/agent harness. SI TUI is the SI organization and operations console.

## Planned interface

```text
┌─────────────────────────────────────────────┐
│ SI-Agents                         RUNNING 3 │
├───────────────┬─────────────────────────────┤
│ Agents        │ Active Team                 │
│ Teams         │ Debugger → Developer → Test │
│ Skills        │                             │
│ Runs          │ Evidence / Events           │
│ Evidence      │ Governance                  │
│ Memory        │ Handoffs                    │
│ Governance    │                             │
│ Organization  │                             │
│ Settings      │                             │
└───────────────┴─────────────────────────────┘
```

## Requirements

- keyboard-first
- fast on Termux
- usable in Codespaces/SSH
- low bandwidth/resource usage
- accessible textual state
- live execution events
- agent/team/run inspection
- governance/evidence inspection
- same Control API as Web

No duplicated runtime or governance implementation is allowed in the TUI.

---

# Phase 42 — Harness Deployment Center

## Objective

Make SI organization deployment into supported agent harnesses understandable, inspectable, and governed.

## Target harnesses

Initial targets include:

- OpenCode
- Codex
- Claude Code
- Cline
- Antigravity
- Universal SI protocol

Future harness adapters should be possible without changing SI core contracts.

## Deployment flow

```text
Select harness
      ↓
Select agents/teams/skills
      ↓
Select environment
      ↓
Compatibility analysis
      ↓
Capabilities/permissions review
      ↓
Unsupported-feature report
      ↓
Governance review
      ↓
Generate deployment
      ↓
Operator-controlled apply
```

Deployment does not itself grant permission. Harness and environment boundaries remain authoritative.

---

# Phase 43 — Full E2E, Security & Release

## Objective

Validate SI-Agents v3 as a complete product rather than a collection of independent features.

## Compatibility matrix

Test combinations across:

```text
Termux × Web × TUI × CLI
Codespaces × Web × TUI × CLI

OpenCode
Codex
Claude Code
Cline
Antigravity
Universal adapter

OmniRoute
```

Not every combination must support every capability, but unsupported combinations must be detected and reported explicitly.

## Security testing

Include adversarial tests for:

- malicious agent personas
- malicious skills
- malicious hooks
- prompt injection
- privilege escalation
- credential leakage
- browser/API abuse
- CSRF/CORS problems
- localhost exposure
- command injection
- path traversal
- impersonation
- tampered handoffs
- unauthorized deployment
- governance bypass
- unsafe configuration imports

## Performance testing

Evaluate:

- hundreds of agents
- thousands of skills
- large event histories
- large evidence stores
- concurrent runs
- large organization graphs
- TUI responsiveness
- Web UI responsiveness
- API throughput

## Release verification

Release acceptance should include:

- package/wheel build
- clean installation
- CLI smoke tests
- Web startup test
- TUI startup test
- catalog validation
- persona validation
- skill validation
- governance tests
- security scanner tests
- adapter conformance tests
- environment tests
- E2E workflows
- regression suite
- documentation consistency

A v3 phase is not complete merely because code exists. Acceptance criteria, tests, CI, installation, runtime behavior, and security evidence must support the completion claim.

---

# 3. Cross-phase dependencies

The intended dependency chain is:

```text
29 Personas
   ↓
30 Skills
   ↓
31 Rules/Hooks/Events
   ↓
32 Memory/Knowledge
   ↓
33 Governance/Security
   ↓
34 Organization Expansion
   ↓
35 Control API
   ↓
36 Web Foundation
   ↓
37 Control Center
   ↓
38 Visual Organization/Workflow
   ↓
39 Agent Builder
   ↓
40 Evidence/Observability
   ↓
41 TUI
   ↓
42 Harness Deployment
   ↓
43 E2E/Security/Release
```

Some implementation work may be developed in parallel where contracts are already stable, but the dependency order defines the architectural direction.

---

# 4. What v3 deliberately does not become

SI-Agents v3 should not become:

- a replacement for OpenCode
- a replacement for Codex or Claude Code
- a provider/model router competing with OmniRoute
- a cloud-only SaaS control plane
- an opaque UI-only agent builder
- an unrestricted arbitrary-command automation engine
- a permission system duplicated inside individual agents
- a collection of copied third-party agent prompts
- a system where Markdown silently grants executable capabilities

The core remains vendor-neutral, evidence-first, governance-controlled, and portable.

---

# 5. Reference projects and design learning

ECC (`affaan-m/ECC`) and Agency Agents (`msitarzewski/agency-agents`) remain ongoing reference projects for v3.

SI-Agents should continue to inspect their current source, architecture, agents, skills, workflows, hooks, rules, tests, issues, pull requests, releases, and relevant changes when materially relevant.

Useful patterns should be generalized rather than copied blindly.

Particular patterns worth preserving as references include:

- rich Markdown agent personas
- separation of agents, skills, rules, hooks, and memory
- team composition/orchestration
- dynamic workflows and quality gates
- portable memory formats
- security/configuration scanning
- canonical organization/catalog sources
- visual agent catalogs
- agent customization/install workflows

SI-Agents should retain its own architectural identity, especially its typed governance, evidence model, runtime interoperability, environment boundaries, and OmniRoute separation.

---

# 6. v3 completion definition

SI-Agents v3 should be considered complete only when the system can demonstrate the following end-to-end behavior:

```text
User
 ↓
CLI / SI TUI / Local Web App
 ↓
SI Control API
 ↓
SI Organization
 ├─ Markdown Personas
 ├─ Typed Contracts
 ├─ Teams
 ├─ Skills
 ├─ Rules
 ├─ Hooks
 ├─ Memory
 ├─ Knowledge
 └─ Governance
 ↓
SI Runtime
 ↓
Harness Adapter
 ↓
Termux / Codespaces
 ↓
OmniRoute
 ↓
Model Provider
```

The execution must produce an inspectable chain of events and evidence, enforce governance, preserve security boundaries, and remain portable across supported environments and harnesses.

---

# 7. Relationship to v2

SI-Agents v3 builds on, rather than replaces, the v2 foundation.

The completed v2/post-v2 work already provides the critical base for:

- agent organization
- teams and workflow DAGs
- universal harness contracts
- OpenCode integration
- OmniRoute integration
- Termux runtime
- GitHub Codespaces runtime
- `si` CLI and setup
- cross-environment handoff
- evidence and governance boundaries

Phase 28 established explicit, integrity-protected cross-environment handoff state while keeping target environments authoritative. v3 should extend this model rather than introducing a hidden synchronization authority.

---

# 8. Implementation discipline

For every v3 phase:

1. Inspect the current repository state.
2. Inspect relevant existing contracts and tests.
3. Review current ECC/Agency Agents patterns when relevant.
4. Define the contract and acceptance criteria.
5. Implement the smallest maintainable change.
6. Add unit/integration/adversarial tests.
7. Run lint/type/static checks applicable to the project.
8. Run the complete regression suite.
9. Build and install artifacts where applicable.
10. Verify real runtime behavior.
11. Inspect CI output and fix discovered defects.
12. Update architecture documentation.
13. Record verification evidence.
14. Only then declare the phase complete.

Documentation must never claim functionality that CI or runtime evidence has not verified.

---

# 9. Roadmap summary

| Phase | Area | Target outcome |
|---|---|---|
| 29 | Agent Personas | Rich Markdown personas + typed contracts |
| 30 | Skills | Portable, versioned, governed skills |
| 31 | Rules/Hooks | Controlled event and policy automation |
| 32 | Memory/Knowledge | Scoped, provenance-aware knowledge |
| 33 | Governance/Security | Unified security and authorization center |
| 34 | Organization | Expanded SI-native agent organization |
| 35 | Control API | Stable runtime/control boundary |
| 36 | Web Foundation | Localhost-first Web application |
| 37 | Control Center | Full visual SI operator dashboard |
| 38 | Visualization | Organization and workflow graphs |
| 39 | Agent Builder | Visual agent creation/customization/testing |
| 40 | Evidence | Deep run/evidence observability |
| 41 | TUI | First-class terminal operator console |
| 42 | Deployment | Governed harness deployment center |
| 43 | Release | Full E2E, security, performance and release validation |

**This document is the planning baseline for SI-Agents v3. Implementation status must be updated only as phases become actually implemented and verified.**
