"""Safe automation execution with retries, idempotency, and governance gates."""

from collections.abc import Callable
from datetime import UTC, datetime
from time import sleep
from uuid import uuid4

from core.automation.models import AutomationJob, RunRecord, RunStatus
from core.governance.engine import GovernanceEngine
from core.governance.models import DecisionStatus, GovernanceRequest, RiskLevel

Action = Callable[[dict[str, object]], None]
Condition = Callable[[AutomationJob], bool]
Clock = Callable[[], datetime]
Sleeper = Callable[[float], None]


class AutomationRunner:
    """Execute registered actions while keeping policy and retry behavior explicit."""

    def __init__(
        self,
        actions: dict[str, Action] | None = None,
        *,
        governance: GovernanceEngine | None = None,
        clock: Clock | None = None,
        sleeper: Sleeper | None = None,
    ) -> None:
        self.actions = actions or {}
        self.governance = governance or GovernanceEngine()
        self.clock = clock or (lambda: datetime.now(UTC))
        self.sleeper = sleeper or sleep
        self._completed_keys: set[str] = set()
        self._history: list[RunRecord] = []

    @property
    def history(self) -> tuple[RunRecord, ...]:
        return tuple(self._history)

    def execute(
        self,
        job: AutomationJob,
        *,
        condition: Condition | None = None,
        governance_request: GovernanceRequest | None = None,
    ) -> RunRecord:
        started = self.clock()
        key = job.idempotency_key
        if key is not None and key in self._completed_keys:
            return self._record(job, RunStatus.SKIPPED, started, 0, "idempotency key already completed")
        if condition is not None and not condition(job):
            return self._record(job, RunStatus.SKIPPED, started, 0, "precondition not satisfied")
        if job.action not in self.actions:
            return self._record(job, RunStatus.FAILED, started, 0, "action is not registered")

        request = governance_request or GovernanceRequest(
            action=job.governance_action or job.action,
            risk=RiskLevel.LOW,
        )
        decision = self.governance.decide(request)
        if decision.status != DecisionStatus.ALLOW:
            status = RunStatus.APPROVAL_REQUIRED if decision.status == DecisionStatus.APPROVAL_REQUIRED else RunStatus.SKIPPED
            return self._record(job, status, started, 0, "; ".join(decision.reasons), decision.status.value)

        attempts = 0
        last_error = ""
        for attempt in range(1, job.retry.max_attempts + 1):
            attempts = attempt
            try:
                self.actions[job.action](job.payload)
            except Exception as exc:  # action failures are recorded, not swallowed silently
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < job.retry.max_attempts:
                    self.sleeper(job.retry.delay_for(attempt))
                    continue
                return self._record(job, RunStatus.FAILED, started, attempts, last_error, decision.status.value)
            if key is not None:
                self._completed_keys.add(key)
            return self._record(job, RunStatus.SUCCESS, started, attempts, "completed", decision.status.value)
        return self._record(job, RunStatus.FAILED, started, attempts, last_error or "execution failed")

    def _record(
        self,
        job: AutomationJob,
        status: RunStatus,
        started: datetime,
        attempts: int,
        message: str,
        decision_status: str | None = None,
    ) -> RunRecord:
        record = RunRecord(
            run_id=str(uuid4()),
            job_id=job.job_id,
            status=status,
            started_at=started,
            finished_at=self.clock(),
            attempts=attempts,
            message=message,
            idempotency_key=job.idempotency_key,
            decision_status=decision_status,
        )
        self._history.append(record)
        return record
