from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from core.runtime.events import EventBus
from core.runtime.execution import AuthorizedTask, ExecutionRuntime, ExecutionStore, State
from core.runtime.scheduler import ParallelScheduler, ScheduleState


class TrackingAdapter:
    def __init__(self, delay: float = 0.03, fail: set[str] | None = None) -> None:
        self.delay = delay
        self.fail = fail or set()
        self.lock = threading.Lock()
        self.active = 0
        self.maximum = 0
        self.started: list[str] = []

    def invoke(self, task, cancel_event):
        with self.lock:
            self.active += 1
            self.maximum = max(self.maximum, self.active)
            self.started.append(task.task_id)
        try:
            end = time.monotonic() + self.delay
            while time.monotonic() < end:
                if cancel_event.is_set():
                    raise RuntimeError("cancelled")
                time.sleep(0.002)
            if task.task_id in self.fail:
                raise RuntimeError("planned failure")
            return {"task_id": task.task_id}
        finally:
            with self.lock:
                self.active -= 1


def make_runtime(tmp_path: Path, bus: EventBus | None = None):
    store = ExecutionStore(tmp_path / "runtime.db", event_bus=bus)
    return store, ExecutionRuntime(store)


def test_parallelism_is_bounded_and_all_tasks_complete(tmp_path: Path):
    bus = EventBus(str(tmp_path / "events.db"))
    store, runtime = make_runtime(tmp_path, bus)
    adapter = TrackingAdapter()
    scheduler = ParallelScheduler(runtime, adapter, max_workers=3, path=str(tmp_path / "schedule.db"), event_bus=bus)
    for i in range(8):
        scheduler.submit(AuthorizedTask(f"task-{i}", {"value": i}))
    items = scheduler.drain(timeout=5)
    assert all(item.state == ScheduleState.SUCCEEDED for item in items)
    assert adapter.maximum <= 3
    assert adapter.maximum >= 2
    assert len(adapter.started) == 8
    scheduler.close()
    store.close()
    bus.close()


def test_dependencies_gate_execution_and_failure_blocks_descendants(tmp_path: Path):
    store, runtime = make_runtime(tmp_path)
    adapter = TrackingAdapter(fail={"root"})
    scheduler = ParallelScheduler(runtime, adapter, max_workers=2, path=str(tmp_path / "schedule.db"))
    root = scheduler.submit(AuthorizedTask("root", {}))
    child = scheduler.submit(AuthorizedTask("child", {}), depends_on=(root.execution_id,))
    grandchild = scheduler.submit(AuthorizedTask("grandchild", {}), depends_on=(child.execution_id,))
    items = scheduler.drain(timeout=5)
    by_id = {item.execution_id: item for item in items}
    assert by_id[root.execution_id].state == ScheduleState.FAILED
    assert by_id[child.execution_id].state == ScheduleState.BLOCKED
    assert by_id[grandchild.execution_id].state == ScheduleState.BLOCKED
    assert adapter.started == ["root"]
    scheduler.close()
    store.close()


def test_priority_orders_ready_work(tmp_path: Path):
    store, runtime = make_runtime(tmp_path)
    adapter = TrackingAdapter(delay=0.01)
    scheduler = ParallelScheduler(runtime, adapter, max_workers=1, path=str(tmp_path / "schedule.db"), aging_seconds=1000)
    low = scheduler.submit(AuthorizedTask("low", {}), priority=0)
    scheduler.submit(AuthorizedTask("high", {}), priority=10)
    scheduler.drain(timeout=5)
    assert adapter.started[0] == "high"
    assert scheduler.get(low.schedule_id).state == ScheduleState.SUCCEEDED
    scheduler.close()
    store.close()


def test_cancel_waiting_item_does_not_invoke_adapter(tmp_path: Path):
    store, runtime = make_runtime(tmp_path)
    adapter = TrackingAdapter(delay=0.05)
    scheduler = ParallelScheduler(runtime, adapter, max_workers=1, path=str(tmp_path / "schedule.db"))
    scheduler.submit(AuthorizedTask("first", {}))
    second = scheduler.submit(AuthorizedTask("second", {}))
    scheduler.start()
    time.sleep(0.01)
    scheduler.cancel(second.schedule_id)
    scheduler.drain(timeout=5)
    assert scheduler.get(second.schedule_id).state == ScheduleState.CANCELLED
    assert "second" not in adapter.started
    assert runtime.store.get(second.execution_id).state == State.CANCELLED
    scheduler.close()
    store.close()


def test_scheduler_persistence_reopens_waiting_queue(tmp_path: Path):
    db = str(tmp_path / "schedule.db")
    store, runtime = make_runtime(tmp_path)
    adapter = TrackingAdapter(delay=0.01)
    scheduler = ParallelScheduler(runtime, adapter, max_workers=1, path=db)
    item = scheduler.submit(AuthorizedTask("persisted", {}))
    assert scheduler.get(item.schedule_id).state == ScheduleState.WAITING
    scheduler.close()
    store.close()

    store2, runtime2 = make_runtime(tmp_path)
    scheduler2 = ParallelScheduler(runtime2, adapter, max_workers=1, path=db)
    assert scheduler2.get(item.schedule_id).state == ScheduleState.WAITING
    scheduler2.drain(timeout=5)
    assert scheduler2.get(item.schedule_id).state == ScheduleState.SUCCEEDED
    scheduler2.close()
    store2.close()


def test_scheduler_events_are_durable(tmp_path: Path):
    bus = EventBus(str(tmp_path / "events.db"))
    store, runtime = make_runtime(tmp_path, bus)
    adapter = TrackingAdapter(delay=0.005)
    scheduler = ParallelScheduler(runtime, adapter, max_workers=1, path=str(tmp_path / "schedule.db"), event_bus=bus)
    item = scheduler.submit(AuthorizedTask("events", {}))
    scheduler.drain(timeout=5)
    types = [event.event_type for event in bus.stream("execution", item.execution_id)]
    assert "scheduler.queued" in types
    assert "scheduler.started" in types
    assert "scheduler.succeeded" in types
    scheduler.close()
    store.close()
    bus.close()


def test_invalid_configuration_fails_closed(tmp_path: Path):
    store, runtime = make_runtime(tmp_path)
    adapter = TrackingAdapter()
    with pytest.raises(ValueError):
        ParallelScheduler(runtime, adapter, max_workers=0)
    scheduler = ParallelScheduler(runtime, adapter, path=str(tmp_path / "schedule.db"))
    with pytest.raises(ValueError):
        scheduler.submit(AuthorizedTask("orphan", {}), depends_on=("missing",))
    scheduler.close()
    store.close()
