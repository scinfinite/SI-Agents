"""Phase 45 durable event/state architecture tests."""
from concurrent.futures import ThreadPoolExecutor

import pytest

from core.runtime.events import EventBus
from core.runtime.execution import AuthorizedTask, ExecutionRuntime, ExecutionStore, State


def test_append_orders_per_aggregate_and_replays(tmp_path):
    bus = EventBus(str(tmp_path / "events.db"))
    first = bus.append("accepted", "execution", "e1", {"state": "accepted"}, correlation_id="c1")
    second = bus.append("queued", "execution", "e1", {"state": "queued"}, correlation_id="c1", causation_id=first.event_id)
    assert (first.sequence, second.sequence) == (0, 1)
    assert [e.event_type for e in bus.stream("execution", "e1")] == ["accepted", "queued"]
    seen = []
    assert bus.replay(seen.append) == 2
    assert [e.event_id for e in seen] == [first.event_id, second.event_id]
    bus.close()


def test_event_id_is_idempotent_but_conflicts_fail(tmp_path):
    bus = EventBus(str(tmp_path / "events.db"))
    event = bus.append("accepted", "task", "t1", {"x": 1}, event_id="evt-1", correlation_id="c")
    assert bus.append("accepted", "task", "t1", {"x": 1}, event_id="evt-1", correlation_id="c") == event
    with pytest.raises(ValueError, match="conflicts"):
        bus.append("failed", "task", "t1", {"x": 2}, event_id="evt-1", correlation_id="c")


def test_persistence_and_correlation_survive_reopen(tmp_path):
    path = tmp_path / "events.db"
    bus = EventBus(str(path))
    bus.append("started", "execution", "e1", {"safe": True}, correlation_id="corr")
    bus.close()
    reopened = EventBus(str(path))
    assert reopened.event_count() == 1
    assert reopened.by_correlation("corr")[0].payload == {"safe": True}


def test_projection_is_replayable_and_checkpointed(tmp_path):
    bus = EventBus(str(tmp_path / "events.db"))
    bus.append("started", "execution", "e1", {"state": "running"}, correlation_id="c")
    bus.append("completed", "execution", "e1", {"state": "succeeded"}, correlation_id="c")
    calls = []

    def reduce_state(state, event):
        calls.append(event.event_id)
        return {"state": event.payload["state"]}

    assert bus.project("execution-state", reduce_state) == 2
    assert bus.get_projection("execution-state", "execution", "e1") == {"state": "succeeded"}
    assert bus.project("execution-state", reduce_state) == 0
    assert len(calls) == 2


def test_projection_can_process_multiple_aggregates(tmp_path):
    bus = EventBus(str(tmp_path / "events.db"))
    bus.append("accepted", "execution", "e1", {"state": "accepted"})
    bus.append("accepted", "execution", "e2", {"state": "accepted"})
    bus.project("states", lambda state, event: {"state": event.payload["state"]})
    assert bus.get_projection("states", "execution", "e1") == {"state": "accepted"}
    assert bus.get_projection("states", "execution", "e2") == {"state": "accepted"}


def test_concurrent_appends_preserve_unique_order(tmp_path):
    bus = EventBus(str(tmp_path / "events.db"))

    def append(i):
        return bus.append("delta", "execution", "e1", {"i": i}, correlation_id="c")

    with ThreadPoolExecutor(max_workers=8) as pool:
        events = list(pool.map(append, range(32)))
    assert sorted(e.sequence for e in events) == list(range(32))
    assert len({e.event_id for e in events}) == 32
    assert len(bus.stream("execution", "e1")) == 32


def test_invalid_event_inputs_fail_closed(tmp_path):
    bus = EventBus(str(tmp_path / "events.db"))
    with pytest.raises(ValueError):
        bus.append("", "execution", "e1", {})
    with pytest.raises(ValueError):
        bus.append("started", "", "e1", {})
    with pytest.raises(ValueError):
        bus.stream("execution", "e1", -2)


def test_execution_runtime_emits_canonical_lifecycle_events(tmp_path):
    bus = EventBus(str(tmp_path / "events.db"))
    store = ExecutionStore(str(tmp_path / "runtime.db"), event_bus=bus)
    runtime = ExecutionRuntime(store)

    class Adapter:
        def invoke(self, task, cancel_event):
            return {"answer": 42}

        def cancel(self, execution_id):
            pass

    execution = runtime.accept(AuthorizedTask("task-1", {"input": 6}))
    assert runtime.run(execution.execution_id, Adapter()).state == State.SUCCEEDED
    events = bus.stream("execution", execution.execution_id)
    assert [event.event_type for event in events] == [
        "execution.accepted", "execution.queued", "execution.running", "execution.succeeded"
    ]
    assert all(event.correlation_id == execution.execution_id for event in events)
    assert events[-1].payload["to"] == "succeeded"
