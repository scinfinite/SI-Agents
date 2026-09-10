from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class TradeoffOption:
    name: str
    benefits: tuple[str, ...] = ()
    costs: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    score: float = 0.0
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Trade-off option name must not be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Trade-off score must be between 0 and 1")


@dataclass(frozen=True)
class TradeoffAnalysis:
    decision: str
    options: tuple[TradeoffOption, ...]
    selected: str
    rationale: str
    uncertainty: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.decision.strip() or not self.selected.strip():
            raise ValueError("Decision and selected option must not be empty")
        if not any(option.name == self.selected for option in self.options):
            raise ValueError("Selected option must be present in options")


class TradeoffEngine:
    def analyze(self, decision: str, options: tuple[TradeoffOption, ...], *, rationale: str, uncertainty: tuple[str, ...] = ()) -> TradeoffAnalysis:
        if not options:
            raise ValueError("Trade-off analysis requires at least one option")
        selected = max(options, key=lambda option: (option.score, option.name))
        return TradeoffAnalysis(decision, options, selected.name, rationale, uncertainty)
