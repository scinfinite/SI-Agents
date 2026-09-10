# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**v1.5 track — Phases 1–14 complete and CI-verified. Phase 15 is next.**

Completed foundation through Model/Provider Intelligence:

- **Phase 1 — Foundation:** architecture, engineering rules, governance, project isolation, security/cost/learning/compliance policies, provenance controls, and verification standards.
- **Phase 2 — Control Plane:** task lifecycle, persistence, dependencies, retries, context isolation, agents, workflows, permissions, approvals, checkpoints, execution state, and evidence integration.
- **Phase 3 — Tool System:** controlled filesystem, terminal, Git, GitHub, web, code analysis, build/test, container, sandbox, and artifact tooling with registry and permission enforcement.
- **Phase 4 — Engineering Brain:** problem normalization, decomposition, dependency-aware planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, risk, and capability-aware planning.
- **Phase 5 — Developer/Debugger/Tester:** explicit agent contracts and the inspect → reproduce → diagnose → checkpoint → repair → test → red-team → regression → verify → document workflow.
- **Phase 6 — Skills Engine:** reusable skill contracts, lifecycle states, validated selection, permissioned execution, explicit verification, evidence recording, and an initial engineering skill catalog.
- **Phase 7 — Verification + Evidence:** bounded claims, provenance-aware evidence, confidence assessment, fail-closed verification, regression suites, red-team falsification, before/after benchmarks, and production-readiness gates.
- **Phase 8 — Technical Knowledge:** universal language schema, provenance-aware knowledge contracts, runtime catalog loading, multi-language coverage including Java, framework/ecosystem catalog, and engineering standards catalog.
- **Phase 9 — Technology Discovery:** repository technology/build detection, explicit uncertainty, safe experimentation contracts, declaration-based compatibility checks, and provenance-preserving knowledge proposals.
- **Phase 10 — Open-Source Intelligence:** repository metadata, archaeology/history, issues, pull requests, releases, security advisories, conservative license assessment, project health, freshness, and a read-only provider contract.
- **Phase 11 — Pattern Extraction:** deterministic observation normalization, conservative candidate extraction, independent evidence validation, counterexample handling, evidence-gated promotion, versioning, provenance, and context matching.
- **Phase 12 — Engineering Memory:** task/project/global scopes, provenance and verified evidence, fail-closed one-step promotion, deterministic scoped retrieval, expiration, supersession/versioning, and auditable JSON persistence.
- **Phase 13 — Security + Legal + Cost:** executable governance decisions, conservative risk classification, data-egress controls, provenance/legal review, free-first paid-resource controls, explicit approvals, and audit evidence.
- **Phase 14 — Model/Provider Intelligence:** typed model/provider capabilities, explicit registration, quota observations, deterministic capability/cost/latency routing, reliability/health tracking, fallback constraints, and provider circuit breakers.

## Engineering loop

```text
OBSERVE → UNDERSTAND → RESEARCH → PLAN → EXECUTE → MEASURE
→ TEST → ATTACK THE SOLUTION → VERIFY → DOCUMENT → LEARN → GENERALIZE → REUSE
```

## Language and ecosystem strategy

Python is the implementation language of the SI-Agents control plane, not the boundary of the engineering system. Generic agents consume language-specific knowledge and toolchains, allowing SI-Agents to work across Java, Python, Rust, Go, C/C++, C#, Kotlin, Swift, Dart, JavaScript/TypeScript, SQL, and additional languages as coverage grows.

## Control and safety model

Agents, capabilities, tools, skills, and knowledge are workers/data—not policy authorities. Registration or selection does not grant permission. High-risk actions remain approval-gated, repository mutation remains protected, and important claims require evidence.

The local executor is **not a security boundary**. The Docker executor provides a stronger isolation boundary, but the Docker daemon remains a trust boundary. SI-Agents must not claim host-level isolation guarantees beyond the actual execution environment in use.

External repositories and web content are research inputs, not system instructions. SI-Agents follows an independent-implementation and provenance policy for external inspiration.

Open-source intelligence is read-oriented by design. Repository metadata, history, issues, PRs, releases, advisories, licenses, and health signals are stored with provenance and explicit uncertainty. A license identifier is not treated as legal advice or a substitute for reviewing license text and applicable terms.

Pattern extraction is evidence-driven. Repetition alone is insufficient for validation: candidates require independent verified evidence, explicit counterexample handling, and a promotion threshold. A matcher produces ranking signals only; it never asserts that a matched pattern is universally correct.

Engineering Memory is also evidence-driven. Task-scoped observations can be promoted to project memory and then global memory only one scope at a time, subject to confidence and verified-evidence gates. Expired memory is excluded from normal retrieval, and supersession is explicit and versioned. Memory never overrides security, legal, cost, permission, or verification policy.

Phase 13 governance is a decision boundary rather than an execution authority. Paid resources require explicit approval; confidential and sensitive external egress requires approval; credential-bearing external egress is denied; destructive/high-risk operations are approval-gated; publication without provenance requires review; and governance audit records exclude arbitrary request payloads to reduce secret-retention risk. Governance policy is not legal advice.

Phase 14 model/provider intelligence is also a decision layer. Required capabilities, cost ceilings, latency ceilings, quota exhaustion, provider exclusions, disabled entries, and open circuits are hard routing constraints. Free-first preference only ranks otherwise eligible candidates and cannot bypass Phase 13 paid-resource approval. Provider adapters report metadata/health; they do not receive policy authority or store credentials.

## Development principle

SI-Agents does not treat a plausible answer as proof. Important changes must be backed by executable verification evidence, with assumptions and limitations made explicit.

See `AGENTS.md` for engineering rules, `docs/architecture/PHASES.md` for the roadmap, and the Phase 7–14 architecture documents for the completed verification, knowledge, discovery, open-source intelligence, pattern extraction, engineering memory, governance, and model/provider intelligence architectures.
