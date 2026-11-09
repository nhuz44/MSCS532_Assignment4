"""Reproducible comparisons of pure-Python sorting implementations."""
import csv
import platform
import random
import statistics
import sys
import time
from pathlib import Path

from heapsort import heap_sort
from comparison_sorts import quick_sort, merge_sort

ROOT = Path(__file__).resolve().parent
SIZES = (500, 2000, 6000)
DISTRIBUTIONS = ("Random", "Sorted", "Reverse sorted", "Repeated values")
TRIALS = 7
SORTERS = (
    ("Heapsort", heap_sort),
    ("Randomized Quicksort", quick_sort),
    ("Merge Sort", merge_sort),
)


def input_data(distribution: str, size: int) -> list[int]:
    rng = random.Random(1200 + size)
    if distribution == "Random":
        return [rng.randrange(-5 * size, 5 * size) for _ in range(size)]
    if distribution == "Sorted":
        return list(range(size))
    if distribution == "Reverse sorted":
        return list(range(size, 0, -1))
    if distribution == "Repeated values":
        return [rng.randrange(0, 12) for _ in range(size)]
    raise ValueError(distribution)


def run_benchmark() -> None:
    rows = []
    for distribution in DISTRIBUTIONS:
        for n in SIZES:
            data = input_data(distribution, n)
            expected = sorted(data)
            for name, sorter in SORTERS:
                # Warm up interpreter caches; excluded from measurement.
                warm = data.copy()
                if name == "Randomized Quicksort":
                    sorter(warm, seed=700)
                else:
                    sorter(warm)
                assert warm == expected, f"incorrect warmup: {name}"

                observations = []
                for trial in range(TRIALS):
                    values = data.copy()  # Input copying excluded from timing.
                    start = time.perf_counter_ns()
                    if name == "Randomized Quicksort":
                        sorter(values, seed=700 + trial)
                    else:
                        sorter(values)
                    duration_ms = (time.perf_counter_ns() - start) / 1e6
                    if values != expected:
                        raise AssertionError(f"incorrect output: {name}/{distribution}/{n}")
                    observations.append(duration_ms)
                row = [name, distribution, n,
                       round(statistics.median(observations), 4),
                       round(min(observations), 4),
                       round(max(observations), 4), TRIALS]
                rows.append(row)
                print(f"{name:21s} {distribution:15s} n={n:5d}: median {row[3]:8.4f} ms")
    with (ROOT / 'benchmark_results.csv').open('w', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(('algorithm', 'dataset', 'n', 'median_time_ms',
                         'min_time_ms', 'max_time_ms', 'trials'))
        writer.writerows(rows)
    environment = (
        f"Platform: {platform.platform()}\n"
        f"Python: {sys.version.split()[0]}\n"
        f"Processor: {platform.machine()}\n"
        f"Timing: perf_counter_ns; median of {TRIALS} trials in milliseconds\n"
        f"Sizes: {SIZES}; copied input before timing; no third-party sort functions\n"
        "Distribution seeds fixed per n; randomized-pivot seed differs per trial\n"
        "All benchmark algorithms are Python implementations, not built-in sorted().\n"
    )
    (ROOT / 'environment.txt').write_text(environment)
    print('Saved benchmark_results.csv and environment.txt')


if __name__ == '__main__':
    run_benchmark()
