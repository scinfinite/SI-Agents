from core.patterns import (
    Counterexample,
    EngineeringPattern,
    PatternCategory,
    PatternEvidence,
    PatternExtractor,
    PatternMatcher,
    PatternNormalizer,
    PatternObservation,
    PatternRegistry,
    PatternStatus,
    PatternValidator,
)


def observation(example: str, source: str, *, verified: bool = True) -> PatternObservation:
    evidence = PatternEvidence(
        source=source,
        example_id=example,
        claim="Observed outcome satisfies the expected behavior",
        verified=verified,
    )
    return PatternObservation(
        example_id=example,
        source=source,
        category=PatternCategory.DEBUGGING,
        problem="isolate a failing boundary",
        context="service boundary",
        mechanism="add an explicit diagnostic boundary",
        outcome="failure becomes attributable to one boundary",
        tags=("diagnostics", "boundary"),
        evidence=(evidence,),
    )


def test_normalizer_is_deterministic_and_case_insensitive() -> None:
    assert PatternNormalizer.normalize_text("  Hello, WORLD! ") == "hello world"
    assert PatternNormalizer.normalize_tags(("Z", "a", "a")) == ("a", "z")
    assert PatternNormalizer.signature(
        category="Debugging", problem="A", mechanism="B", tags=("X",)
    ) == PatternNormalizer.signature(
        category="debugging", problem=" a ", mechanism="b", tags=("x",)
    )


def test_extractor_creates_candidate_from_repeated_observations() -> None:
    patterns = PatternExtractor().extract((observation("one", "repo-a"), observation("two", "repo-b")))
    assert len(patterns) == 1
    assert patterns[0].status is PatternStatus.CANDIDATE
    assert set(patterns[0].provenance) == {"repo-a", "repo-b"}
    assert patterns[0].confidence == 0.9


def test_validator_fail_closed_for_single_source() -> None:
    pattern = PatternExtractor().extract((observation("one", "repo-a"),))[0]
    result = PatternValidator().validate(pattern)
    assert result.status is PatternStatus.EXPERIMENTAL
    assert not result.promotable
    assert result.independent_sources == 1
    assert "two independent sources" in " ".join(result.reasons)


def test_validator_requires_verified_evidence() -> None:
    pattern = PatternExtractor().extract(
        (observation("one", "repo-a", verified=False), observation("two", "repo-b", verified=False))
    )[0]
    result = PatternValidator().validate(pattern)
    assert result.status is PatternStatus.EXPERIMENTAL
    assert result.verified_evidence == 0


def test_validator_accepts_independent_verified_examples() -> None:
    pattern = PatternExtractor().extract((observation("one", "repo-a"), observation("two", "repo-b")))[0]
    result = PatternValidator().validate(pattern)
    assert result.status is PatternStatus.VALIDATED
    assert result.promotable
    assert result.independent_examples == 2


def test_counterexample_blocks_promotion() -> None:
    base = observation("one", "repo-a")
    second = observation("two", "repo-b")
    pattern = PatternExtractor().extract((base, second))[0]
    pattern = EngineeringPattern(
        name=pattern.name,
        category=pattern.category,
        intent=pattern.intent,
        context=pattern.context,
        mechanism=pattern.mechanism,
        applicability=pattern.applicability,
        contraindications=pattern.contraindications,
        verification_criteria=pattern.verification_criteria,
        provenance=pattern.provenance,
        evidence=pattern.evidence,
        counterexamples=(Counterexample("bad", "fails under load", "repo-c"),),
        confidence=pattern.confidence,
    )
    result = PatternValidator().validate(pattern)
    assert not result.promotable
    assert result.counterexamples == 1


def test_registry_requires_matching_passing_validation() -> None:
    pattern = PatternExtractor().extract((observation("one", "repo-a"), observation("two", "repo-b")))[0]
    registry = PatternRegistry()
    registry.record(pattern)
    result = PatternValidator().validate(pattern)
    promoted = registry.promote(pattern.id, result)
    assert promoted.status is PatternStatus.VALIDATED
    assert promoted.version == 2
    assert registry.get(pattern.id) == promoted


def test_registry_rejects_mismatched_validation() -> None:
    pattern = PatternExtractor().extract((observation("one", "repo-a"), observation("two", "repo-b")))[0]
    registry = PatternRegistry()
    registry.record(pattern)
    result = PatternValidator().validate(pattern)
    wrong = result.__class__(
        pattern_id="other", status=result.status, confidence=result.confidence,
        independent_sources=result.independent_sources, independent_examples=result.independent_examples,
        verified_evidence=result.verified_evidence, counterexamples=result.counterexamples,
        reasons=result.reasons,
    )
    try:
        registry.promote(pattern.id, wrong)
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("mismatched validation must fail")


def test_matcher_never_claims_validation_and_returns_ranked_results() -> None:
    pattern = PatternExtractor().extract((observation("one", "repo-a"), observation("two", "repo-b")))[0]
    matches = PatternMatcher().match(
        (pattern,), category="debugging", context="service boundary", tags=("diagnostics",)
    )
    assert matches[0][0] is pattern
    assert 0.0 <= matches[0][1] <= 1.0
