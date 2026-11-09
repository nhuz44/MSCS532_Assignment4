"""Discrete-time, non-preemptive task scheduler using a max-priority queue."""
from collections import deque
from dataclasses import dataclass
from priority_queue import MaxPriorityQueue, Task


@dataclass(frozen=True, slots=True)
class Execution:
    task_id: str
    priority: int
    arrival_time: int
    start_time: int
    end_time: int
    deadline: int | None
    waiting_time: int
    deadline_met: bool | None


def sample_tasks() -> list[Task]:
    """Fictional IT tasks; timestamps are illustrative integer time units."""
    return [
        Task("precheck-101", 4, 0, 2, 7),
        Task("urgent-health-102", 9, 0, 2, 4),
        Task("network-103", 6, 1, 3, 10),
        Task("firmware-104", 5, 2, 3, 11),
        Task("alert-review-105", 8, 3, 1, 6),
        Task("log-archive-106", 2, 4, 2, 14),
        Task("host-check-107", 7, 6, 2, 11),
        Task("report-108", 1, 7, 1, 16),
    ]


def schedule(tasks: list[Task], *, policy: str = "priority") -> list[Execution]:
    """Schedule all tasks after arrival, without preemption or dependencies.

    policy=priority uses highest priority among ready tasks; policy=fifo
    uses ready tasks' arrival/order. Deadlines are observed, not enforced.
    """
    if policy not in ("priority", "fifo"):
        raise ValueError("policy must be priority or fifo")
    ids = [task.task_id for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("task IDs must be unique")

    ordered = sorted(enumerate(tasks), key=lambda pair: (pair[1].arrival_time, pair[0]))
    queue = MaxPriorityQueue() if policy == "priority" else deque()
    cursor, clock = 0, 0
    result: list[Execution] = []

    while cursor < len(ordered) or queue:
        if not queue and cursor < len(ordered) and clock < ordered[cursor][1].arrival_time:
            clock = ordered[cursor][1].arrival_time
        while cursor < len(ordered) and ordered[cursor][1].arrival_time <= clock:
            task = ordered[cursor][1]
            if policy == "priority":
                queue.insert(task)
            else:
                queue.append(task)
            cursor += 1
        task = queue.extract_max() if policy == "priority" else queue.popleft()
        end = clock + task.duration
        result.append(Execution(
            task_id=task.task_id,
            priority=task.priority,
            arrival_time=task.arrival_time,
            start_time=clock,
            end_time=end,
            deadline=task.deadline,
            waiting_time=clock - task.arrival_time,
            deadline_met=(end <= task.deadline) if task.deadline is not None else None,
        ))
        clock = end
    return result


def metrics(executions: list[Execution]) -> dict:
    n = len(executions)
    deadlines = [x for x in executions if x.deadline_met is not None]
    return {
        "tasks": n,
        "makespan": max((x.end_time for x in executions), default=0),
        "average_wait": sum(x.waiting_time for x in executions) / n if n else 0.0,
        "max_wait": max((x.waiting_time for x in executions), default=0),
        "deadline_misses": sum(x.deadline_met is False for x in deadlines),
        "deadline_count": len(deadlines),
    }
