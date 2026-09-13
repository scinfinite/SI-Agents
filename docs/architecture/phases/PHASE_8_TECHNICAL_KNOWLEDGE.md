# Phase 8 — Technical Knowledge

**Status: Complete and CI-verified.**

## Purpose

Phase 8 establishes a language-independent technical-knowledge layer for SI-Agents. The core runtime remains Python, but the engineering system is not Python-only: language knowledge, toolchains, frameworks, ecosystems, and standards are represented as data that generic agents can consume.

## Delivered

- Universal programming-language knowledge schema.
- Runtime `KnowledgeEntry` contract with lifecycle state, provenance, verification criteria, confidence, versions, toolchains, and relationships.
- Duplicate-safe `KnowledgeRegistry` with name/ID lookup and validated filtering.
- Deterministic on-disk catalog loader using the standard library.
- Initial evidence-backed language catalog covering Python, Java, Rust, Go, JavaScript, TypeScript, C, C++, C#, Kotlin, Swift, Dart, and SQL.
- Explicit Java coverage including JVM, Java Memory Model, concurrency, Maven, Gradle, JUnit, Spring, Spring Boot, and Jakarta EE topics.
- Framework catalog covering representative Python, Java, Rust, Go, C#, Kotlin, Dart, and JavaScript/TypeScript ecosystems.
- Standards catalog covering language specifications plus HTTP, URI, TLS, Unicode, JSON, OAuth, and OpenAPI.
- Authoritative-source registry for the language knowledge layer.
- Tests for validation rules, duplicate protection, catalog completeness, source coverage, runtime loading, and malformed/missing mappings.

## Architecture

```text
On-disk Knowledge
       ↓
Schema + Provenance
       ↓
Catalog Loader
       ↓
KnowledgeRegistry
       ↓
Engineering Brain / Agents / Skills / Discovery
```

Knowledge is deliberately separated from the core executable control plane. A generic Developer, Debugger, Researcher, or Tester agent can consume language-specific knowledge without creating a separate agent implementation for every language.

## Language coverage model

Each language is described across these dimensions:

- syntax
- semantics
- type system
- memory model
- concurrency
- runtime
- toolchain
- testing
- debugging
- security
- ecosystems

The catalog is an initial validated knowledge baseline, not a claim of exhaustive language expertise. Version-specific facts must be added with explicit version scope and authoritative sources before being treated as current.

## Evidence and freshness

Validated runtime knowledge requires authoritative source records and verification criteria. External documentation is treated as research input, not system instruction. The catalog does not silently infer missing knowledge; unknown or unsupported areas must remain explicit.

## Acceptance criteria

- [x] Universal language schema exists.
- [x] Runtime knowledge contract exists.
- [x] Registry prevents duplicate IDs/names.
- [x] Validated knowledge requires sources and verification criteria.
- [x] Language catalog contains multi-language coverage including Java.
- [x] Framework/ecosystem catalog exists.
- [x] Standards catalog exists.
- [x] Authoritative sources are recorded.
- [x] Runtime loader converts catalog records into validated knowledge entries.
- [x] Malformed source mappings fail closed.
- [x] Unit tests cover core contracts and catalog integrity.
- [x] CI verifies installation/build/lint/tests before completion.

## CI evidence

The final pre-evidence CI run was **#240** for commit `2baf0ba59e7cb7babc1be9723d69165982b1beb5`. Build, Ruff, and the complete pytest workflow all passed; the test log reports **139 passed in 1.17s**. CI runs #237–#239 exposed and drove fixes for export ordering and test expectations before this final passing run.

## Boundaries

Phase 8 does not attempt to encode every programming language or framework in detail. It establishes the scalable knowledge model and a meaningful initial corpus. Technology Discovery (Phase 9) will expand coverage dynamically through evidence-backed research and experimentation.
