from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class CapabilityBenchmark:
    capability_id: str
    score: float
    suite: str
    passed: bool
    evidence_id: str | None = None
    id: str = uuid4().hex
    recorded_at: datetime = datetime.now(UTC)

    def __post_init__(self) -> None:
        if not self.capability_id.strip():
            raise ValueError("Capability ID must not be empty")
        if not self.suite.strip():
            raise ValueError("Benchmark suite must not be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Benchmark score must be between 0 and 1")


class CapabilityBenchmarkStore:
    def __init__(self) -> None:
        self._records: dict[str, CapabilityBenchmark] = {}

    def record(self, benchmark: CapabilityBenchmark) -> CapabilityBenchmark:
        if benchmark.id in self._records:
            raise ValueError(f"Benchmark ID already registered: {benchmark.id}")
        self._records[benchmark.id] = benchmark
        return benchmark

    def for_capability(self, capability_id: str) -> tuple[CapabilityBenchmark, ...]:
        return tuple(item for item in self._records.values() if item.capability_id == capability_id)

    def latest(self, capability_id: str) -> CapabilityBenchmark | None:
        records = self.for_capability(capability_id)
        return max(records, key=lambda item: item.recorded_at) if records else None
