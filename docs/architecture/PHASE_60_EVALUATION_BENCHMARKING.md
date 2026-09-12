# Phase 60 — Evaluation + Benchmarking

**Status:** Complete at advanced-hardening level; implementation hardening PR #74 and final synchronized-tree mainline CI #1144 (`34691176676`) passed all repository closure gates.

## Advanced scope

Phase 60 creates a deterministic evaluation authority for golden cases, multi-mode scoring, failure classification, benchmark history, regression detection, human review, weighted experiments, and release gating.

## Contracts

- exact, normalized, containment, JSON-equality, numeric-tolerance, and rubric scoring
- weighted multi-metric cases with explicit thresholds
- reliability, security, latency and cost dimensions
- explicit timeout/tool/model/authorization/security/infrastructure failure taxonomy
- fail-closed scoring for failed, unreliable or insecure samples
- bounded suites and serialized evidence payloads
- deterministic regression detection against named dimension baselines
- cryptographic evidence digest for benchmark reports
- durable benchmark history and human-review aggregation
- deterministic salted experiment assignment with weighted variants
- configurable release gate with score, dimension, regression, cost, and latency budgets
- secret rejection for cases, evaluator outputs, run metadata, and review rationale
- persisted evidence verification for benchmark history
- evaluation remains advisory: it does not grant execution, provider, credential, or approval authority

## Advanced hardening closure

The post-phase audit identified a contract mismatch: cost and latency were documented dimensions but were not enforceable release-gate budgets. The hardening pass added explicit `maximum_cost` and `maximum_latency_ms` policy controls and fail-closed enforcement. It also expanded secret rejection to evaluator outputs/metadata and human-review rationale, added persisted evidence verification, tightened experiment inputs, and rejected empty report generation.

## Verification

tests/test_phase60_evaluation.py covers all scoring modes, tolerance/threshold rules, failure handling, secret/duplicate guards, persisted-evidence tamper detection, output/metadata/review secret rejection, cost/latency release budgets, persistence and review aggregation, regression gates, deterministic A/B assignment, invalid experiment inputs, and report serialization.

Closure requires repository audit, distribution/wheel verification, integration verification, Ruff, compileall, full pytest, documentation synchronization, and final exact-tree mainline CI.
