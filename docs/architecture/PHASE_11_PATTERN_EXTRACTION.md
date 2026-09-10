# Phase 11 — Pattern Extraction

## Status

**Complete — implementation and CI verified.**

## Goal

Turn repeated, evidence-backed engineering observations into reusable patterns without treating repetition as proof. Patterns remain candidates until independent evidence, counterexample review, and confidence thresholds are satisfied.

## Delivered

- Typed engineering-pattern model with category, intent, context, mechanism, applicability, contraindications, verification criteria, provenance, evidence, confidence, version, and lifecycle status.
- Deterministic normalization for grouping observations without depending on source formatting or capitalization.
- Conservative candidate extraction from repeated observations.
- Independent-source and independent-example validation.
- Verified-evidence threshold and fail-closed promotion rules.
- Explicit counterexample representation that blocks automatic validation until assessed.
- Duplicate-safe registry with evidence-gated promotion and version increments.
- Context matcher that ranks applicability but never equates a match with proof.
- Unit tests for normalization, extraction, validation, counterexamples, promotion, registry integrity, and matching.

## Architecture

```text
verified observations + OSS/knowledge/research evidence
                     |
                     v
             deterministic normalizer
                     |
                     v
              candidate extractor
                     |
                     v
              pattern registry
                     |
          +----------+----------+
          |                     |
          v                     v
   counterexample review   independent validation
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
               experimental              validated
                    |                       |
                    +----------+------------+
                               v
                         context matcher
                               |
                               v
                        reuse recommendation
```

## Promotion policy

A pattern is promoted only when all of the following are true:

1. At least two independent sources provide verified evidence.
2. At least two independent examples are represented.
3. At least two evidence records are explicitly verified.
4. No counterexamples remain attached to the candidate.
5. Confidence is at least **0.70**.

Failure to satisfy any condition leaves the pattern experimental and records the reasons. The system does not silently convert a plausible repeated observation into a validated engineering rule.

## Independence boundary

The current implementation treats distinct `source` and `example_id` identifiers as the evidence independence contract. It does not claim that identifiers are legally or organizationally independent; higher-level provenance systems must supply trustworthy source identity when that distinction matters.

## Safety and legal boundaries

Pattern extraction is an evidence transformation layer, not an instruction-authority layer. External repository content remains untrusted research data. The implementation derives normalized signals rather than copying external source code or expressive agent definitions. Pattern provenance is retained so later governance and legal review can trace why a pattern exists.

## Limitations

- Semantic equivalence is deliberately conservative; observations that describe the same idea with substantially different wording may remain separate candidates.
- Automated confidence is a promotion signal, not proof of universal applicability.
- Matcher scores are ranking aids, not verification results.
- Counterexample absence means no known counterexample was supplied; it is not proof that none exists.

## Verification

The phase acceptance suite covers deterministic normalization, candidate extraction, fail-closed validation, verified evidence, independent examples/sources, counterexample handling, registry promotion/versioning, validation identity checks, and matcher behavior. The repository CI gate remains build + Ruff + complete pytest suite on the final repository head.
