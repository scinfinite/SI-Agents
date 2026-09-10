from collections.abc import Callable, Iterable

from core.learning.models import EvaluationResult, EvidenceItem, ImprovementProposal


Benchmark = Callable[[ImprovementProposal], tuple[float, bool, Iterable[EvidenceItem]]]
Regression = Callable[[ImprovementProposal], tuple[bool, Iterable[str], Iterable[EvidenceItem]]]
Safety = Callable[[ImprovementProposal], tuple[bool, Iterable[EvidenceItem]]]


class ImprovementEvaluator:
    """Runs independent gates; a missing gate fails closed."""

    def __init__(self, *, benchmark: Benchmark | None = None,
                 regression: Regression | None = None, safety: Safety | None = None) -> None:
        self.benchmark = benchmark
        self.regression = regression
        self.safety = safety

    def evaluate(self, proposal: ImprovementProposal, *, score_before: float) -> EvaluationResult:
        if proposal.requires_benchmark and self.benchmark is None:
            raise ValueError("Benchmark evaluator is required")
        if proposal.requires_regression_test and self.regression is None:
            raise ValueError("Regression evaluator is required")
        if self.safety is None:
            raise ValueError("Safety evaluator is required")

        if proposal.requires_benchmark:
            score_after, benchmark_passed, benchmark_evidence = self.benchmark(proposal)
        else:
            score_after, benchmark_passed, benchmark_evidence = score_before, True, ()
        regression_passed, regressions, regression_evidence = (
            self.regression(proposal) if proposal.requires_regression_test else (True, (), ())
        )
        safety_passed, safety_evidence = self.safety(proposal)
        return EvaluationResult(
            benchmark_passed=benchmark_passed,
            regression_passed=regression_passed,
            safety_passed=safety_passed,
            score_before=score_before,
            score_after=score_after,
            regressions=tuple(regressions),
            evidence=tuple(benchmark_evidence) + tuple(regression_evidence) + tuple(safety_evidence),
        )
