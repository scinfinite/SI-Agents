# SI-Agents Foundation Architecture

## Purpose

SI-Agents is a reusable, evidence-driven AI engineering system. It is intended to inspect real software, research unfamiliar technologies, plan changes, execute tools, verify outcomes, preserve project isolation, and improve its engineering knowledge under controlled governance.

## Core execution loop

Observe -> Understand -> Research -> Plan -> Execute -> Measure -> Test -> Attack the solution -> Verify -> Document -> Learn -> Generalize -> Reuse

## Architectural layers

- Control plane: orchestration, workflow, state, context, policy, permissions, approvals, checkpoints.
- Engineering intelligence: decomposition, reasoning, hypotheses, root-cause analysis, trade-offs, uncertainty, decisions.
- Agents: specialized engineering roles coordinated by the control plane.
- Skills: reusable procedures with explicit inputs, tools, safety, verification, failure handling, and success criteria.
- Tools: filesystem, terminal, Git, GitHub, web research, code analysis, build/test tooling, containers, and sandboxing.
- Knowledge: programming, software engineering, architectures, technologies, standards, patterns, and validated lessons.
- Governance: security, legal/compliance, cost, permissions, and data handling.
- Verification: tests, builds, regression checks, benchmarks, red-team review, evidence, and production-readiness checks.
- Learning: controlled extraction of lessons and patterns followed by benchmarking, approval, update, and regression testing.

## Evidence policy

Important claims must identify their evidence, source, version/date when relevant, assumptions, risk, confidence, and verification status. Verification states are distinct from inference. A plausible result is not a verified result.

## Project isolation

Project-specific context is isolated from global reusable knowledge. Promotion from project memory to global knowledge requires generalization and evidence-based validation.

## Upstream research

ECC (affaan-m/ECC) and Agency Agents (msitarzewski/agency-agents) are continuous reference projects. SI-Agents should inspect their current implementations and evolution when relevant, extract general engineering patterns, and independently validate any adapted approach.

## Delivery principle

Build incrementally. Do not create a large empty architecture and call it complete. Each phase must produce executable behavior and evidence that its acceptance criteria are satisfied.
