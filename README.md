# SI-Agents

SI-Agents is the governed execution and agent platform for Project-SI. V4 is being built as one authoritative SI Core exposed through Web, TUI, and CLI surfaces.

## Current V4 status

- **Phases 44–51 complete and merged to `main`.**
- **Next:** Phase 52 — Context / Memory Economics.
- Phase 50 baseline: `9222379cfcb091858f0c5dcc1ec1616f933fca38` with final docs CI run `34625819419`.
- Phase 51 final exact-tree CI: run 977 / `34627956634` — green.

## Phase 51 — Checkpoints + Resume

Phase 51 adds durable, append-only SQLite checkpoints with per-execution sequence and lineage, SHA-256 integrity verification, bounded state, secret-like field rejection, and safe resume through the authoritative execution runtime. Resume creates a fresh runtime attempt rather than restoring authority from a snapshot. See `docs/architecture/PHASE_51_CHECKPOINTS_RESUME.md`.

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

A phase is not complete until implementation, adversarial/security tests, documentation synchronization, repository audit, distribution/wheel verification, Ruff, compileall, full pytest, and the final exact-tree CI run are green. Historical phase records preserve phase-time evidence; current/index documents are synchronized after every phase.
