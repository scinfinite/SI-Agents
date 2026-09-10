# Phase 9 — Technology Discovery

**Status: Complete and CI-verified.**

## Purpose

Phase 9 gives SI-Agents a deterministic, evidence-oriented discovery layer for unfamiliar repositories. Discovery identifies technologies from repository declarations, records uncertainty when a detector cannot establish a fact, supports explicitly supplied non-destructive experiments, performs declaration-based compatibility checks, and converts verified observations into knowledge proposals without silently promoting them to validated knowledge.

## Delivered

- Discovery result contracts with lifecycle status, findings, unknowns, and experiments.
- Immutable discovery findings with confidence, source, and verification metadata.
- Detector protocol and duplicate-safe deterministic detector registry.
- Repository detector for common language and build-system markers, including Java/Maven/Gradle, Python, Rust, Go, JavaScript/TypeScript, C#, Kotlin, Dart, and Swift.
- Repository discovery facade for the default detector set.
- Fail-closed scanner behavior: detector failures become explicit unknowns rather than false facts.
- Explicit experiment runner for caller-supplied non-destructive experiments; exceptions and invalid observations fail closed.
- Declaration-based compatibility checks that do not execute untrusted repository code.
- Knowledge-proposal generation that preserves discovery provenance and never auto-promotes discoveries into global validated knowledge.
- Unit and adversarial tests for detector behavior, registry integrity, malformed reports, detector failure, compatibility, experiments, proposal generation, and confidence validation.

## Architecture

```text
Unfamiliar Repository
        ↓
Repository Scanner
        ↓
Registered Detectors
        ↓
Findings + Unknowns
        ↓
Evidence / Verification
        ↓
Compatibility / Experiments
        ↓
Knowledge Proposals
        ↓
Controlled Knowledge Promotion
```

Discovery is intentionally separate from execution. Merely finding `pom.xml`, `package.json`, or another marker is evidence of a declaration, not proof that a toolchain is installed or that the project builds. Stronger claims require explicit compatibility checks or execution in an approved sandbox.

## Safety boundaries

- Repository content is untrusted input.
- Detection does not execute repository-provided code.
- Compatibility checks in the baseline implementation inspect declarations only.
- Experiments must be explicitly supplied by the caller and are not granted additional permissions by discovery.
- Detector failures become unknowns; they never become successful findings.
- Discovery-derived knowledge remains a proposal until the normal knowledge verification/promotion gates are satisfied.

## Initial discovery coverage

The baseline detector recognizes declarations for:

- Python
- Java
- Rust
- Go
- JavaScript
- TypeScript
- C#
- Dart
- Kotlin
- Swift
- Maven
- Gradle
- Cargo
- Go Modules
- npm
- Flutter/Dart
- Swift Package Manager

This is an extensible baseline, not an exhaustive ecosystem detector. Later phases can add package-manager metadata, framework identification, dependency graph analysis, documentation discovery, repository archaeology, and deeper compatibility experiments.

## Acceptance criteria

- [x] Discovery models exist with explicit lifecycle states.
- [x] Findings contain source, confidence, and verification metadata.
- [x] Detector registry is deterministic and duplicate-safe.
- [x] Repository technology/build markers can be discovered without executing code.
- [x] Java and multiple other language ecosystems are discoverable.
- [x] Unknown detector outcomes remain explicit.
- [x] Explicit experiments fail closed on exceptions or invalid observations.
- [x] Compatibility checks do not execute untrusted repository content.
- [x] Discovery can generate provenance-preserving knowledge proposals.
- [x] Discovery cannot silently promote knowledge.
- [x] Tests cover normal and adversarial behavior.
- [x] CI verifies installation, build, lint, and the complete test suite before completion.

## CI evidence

Phase 9 was completed only after the final repository head passed the complete CI workflow. The final run and test count are recorded in the synchronized roadmap and release documentation.

## Next phase

Phase 10 — Open-Source Intelligence will extend discovery from local repository structure into repository history, issues, pull requests, releases, security advisories, licenses, and project health.
