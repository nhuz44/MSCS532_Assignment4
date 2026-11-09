"""Simple demonstration of heapsort, priority updates, and a scheduler."""
from heapsort import heap_sort
from priority_queue import Task, MaxPriorityQueue
from scheduler import sample_tasks, schedule, metrics


def main() -> None:
    numbers = [19, 3, 13, 7, 5, 3, 12]
    print("Original:", numbers)
    heap_sort(numbers)
    print("Heapsort:", numbers)

    queue = MaxPriorityQueue()
    queue.insert(Task("routine-1", 2, 0, 1, 10))
    queue.insert(Task("urgent-2", 7, 0, 1, 4))
    queue.insert(Task("routine-3", 3, 0, 1, 10))
    print("Top task:", queue.peek().task_id)
    queue.increase_key("routine-1", 8)
    print("Top after increase_key:", queue.extract_max().task_id)
    queue.decrease_key("urgent-2", 1)
    print("Remaining queue order:", [queue.extract_max().task_id for _ in range(len(queue))])

    for policy in ("priority", "fifo"):
        executions = schedule(sample_tasks(), policy=policy)
        print(f"\n{policy.upper()} scheduler")
        for run in executions:
            print(f"{run.start_time:2d}-{run.end_time:2d} {run.task_id:20s} priority={run.priority} "
                  f"wait={run.waiting_time} deadline_met={run.deadline_met}")
        print("Summary:", metrics(executions))


if __name__ == "__main__":
    main()
