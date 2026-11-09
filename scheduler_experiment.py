"""Run priority scheduling and FIFO baseline on an identical synthetic workload."""
import csv
from pathlib import Path
from scheduler import sample_tasks, schedule, metrics

ROOT = Path(__file__).resolve().parent


def run_experiment() -> None:
    tasks = sample_tasks()
    summary = []
    detail = []
    for policy in ("priority", "fifo"):
        runs = schedule(tasks, policy=policy)
        m = metrics(runs)
        summary.append([policy, m['tasks'], m['makespan'],
                        f"{m['average_wait']:.3f}", m['max_wait'],
                        m['deadline_misses'], m['deadline_count']])
        for run in runs:
            detail.append([policy, run.task_id, run.priority, run.arrival_time,
                           run.start_time, run.end_time, run.waiting_time,
                           run.deadline if run.deadline is not None else '',
                           '' if run.deadline_met is None else run.deadline_met])
        print(f"{policy:8s}", m)
    with (ROOT / 'scheduler_results.csv').open('w', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(('policy', 'tasks', 'makespan', 'average_wait',
                         'max_wait', 'deadline_misses', 'deadline_count'))
        writer.writerows(summary)
    with (ROOT / 'scheduler_trace.csv').open('w', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(('policy', 'task_id', 'priority', 'arrival_time', 'start_time',
                         'end_time', 'waiting_time', 'deadline', 'deadline_met'))
        writer.writerows(detail)


if __name__ == '__main__':
    run_experiment()
