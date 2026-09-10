# SI-Agents

SI-Agents is an evidence-driven AI engineering system designed to inspect software, diagnose problems, execute controlled changes, verify results, and learn reusable engineering patterns.

## Current status

**Beta — Phases 1–9 complete and CI-verified. Phase 10 is next.**

Completed foundation through Technology Discovery:

- **Phase 1 — Foundation:** architecture, engineering rules, governance, project isolation, security/cost/learning/compliance policies, provenance controls, and verification standards.
- **Phase 2 — Control Plane:** task lifecycle, persistence, dependencies, retries, context isolation, agents, workflows, permissions, approvals, checkpoints, execution state, and evidence integration.
- **Phase 3 — Tool System:** controlled filesystem, terminal, Git, GitHub, web, code analysis, build/test, container, sandbox, and artifact tooling with registry and permission enforcement.
- **Phase 4 — Engineering Brain:** problem normalization, decomposition, dependency-aware planning, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, risk, and capability-aware planning.
- **Phase 5 — Developer/Debugger/Tester:** explicit agent contracts and the inspect → reproduce → diagnose → checkpoint → repair → test → red-team → regression → verify → document workflow.
- **Phase 6 — Skills Engine:** reusable skill contracts, lifecycle states, validated selection, permissioned execution, explicit verification, evidence recording, and an initial engineering skill catalog.
- **Phase 7 — Verification + Evidence:** bounded claims, provenance-aware evidence, confidence assessment, fail-closed verification, regression suites, red-team falsification, before/after benchmarks, and production-readiness gates.
- **Phase 8 — Technical Knowledge:** universal language schema, provenance-aware knowledge contracts, runtime catalog loading, multi-language coverage including Java, framework/ecosystem catalog, and engineering standards catalog.
- **Phase 9 — Technology Discovery:** repository technology/build detection, explicit uncertainty, safe experimentation contracts, declaration-based compatibility checks, and provenance-preserving knowledge proposals.

The latest Phase 9 CI result is recorded in the architecture documentation after the final workflow completes.

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

## Development principle

SI-Agents does not treat a plausible answer as proof. Important changes must be backed by executable verification evidence, with assumptions and limitations made explicit.

See `AGENTS.md` for engineering rules, `docs/architecture/PHASES.md` for the roadmap, and the Phase 7–9 architecture documents for the completed verification, knowledge, and discovery architectures.
