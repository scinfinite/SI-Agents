# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is being built as one authoritative SI Core exposed through Web, TUI, and CLI surfaces.

## Current V4 status

- **Phases 44–51 are complete on the baseline; Phases 46, 47, 49, and 50 have additionally passed an advanced-level hardening audit.**
- Advanced audit CI **#984 (`34671292491`)** passed distribution, wheel verification, repository audit, integration verification, Ruff, and the complete pytest suite.
- The advanced hardening closes scheduler idempotency/DAG safety, OpenCode timeout/SSE safety, team topology/schema safety, and request-bound authorization/metadata safety gaps.
- **Next:** Phase 52 — Context / Memory Economics.

## Advanced-hardened phases

### Phase 46 — Parallel Scheduler + Executor

Advanced hardening now covers explicit execution identity conflicts, runtime/scheduler idempotency, dependency graph cycle defense, bounded concurrency, durable recovery, cancellation finalization, and dependency failure propagation.

### Phase 47 — OpenCode Bridge

Advanced hardening now covers per-request transport timeout propagation, bounded 1 MiB SSE frames, strict session filtering, terminal-event requirements, cancellation, error normalization, and the SI/OpenCode authority boundary.

### Phase 49 — Agent + Team Builder

Advanced hardening now covers schema-versioned deterministic catalogs/manifests, duplicate metadata/definition validation, acyclic handoff graphs, deterministic execution layers, and explicit separation between declarations and runtime authority.

### Phase 50 — Capability Authorization

Advanced hardening now covers request-fingerprint-bound high/critical approvals, approval replay prevention, secret-like metadata rejection, bounded governance input sizes, explicit egress semantics, declared-capability enforcement, scope checks, and fail-closed decisions.

## V4 roadmap

44. Execution Runtime Foundation  
45. Event Bus + State Architecture  
46. Parallel Scheduler + Executor  
47. OpenCode Bridge  
48. OmniRoute Integration  
49. Agent + Team Builder  
50. Capability Authorization  
51. Checkpoints + Resume  
52. Context / Memory Economics  
53. Persistent Sessions  
54. Human-in-the-Loop  
55. Durable Waiting + Scheduling  
56. Intelligent Routing + Economics  
57. Security Platform  
58. Workspace / Worktree Lifecycle  
59. Observability  
60. Evaluation + Benchmarking  
61. Continuous Improvement  
62. Cross-Runtime / Cross-Harness  
63. Ecosystem / Marketplace  
64. SDK / Developer Platform  
65. Workflow + Automation  
66. Advanced Web Control Plane  
67. Advanced TUI Control Center  
68. Advanced CLI Platform  
69. npm Distribution + Setup  
70. End-to-End Production Validation  
71. Final Production Hardening

## Engineering gate

A phase is not complete until implementation, adversarial/security tests, documentation synchronization, repository audit, distribution/wheel verification, Ruff, compileall, full pytest, and the final exact-tree CI run are green. Historical phase records preserve phase-time evidence; current/index documents are synchronized after every phase and after any cross-phase hardening audit.
