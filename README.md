# MSCS532 Assignment 4: Heap Data Structures

**Course:** MSCS-532-B01 — Algorithms and Data Structures

## Project overview

This project implements Heapsort and a binary-heap priority queue in Python. I compared Heapsort with Quicksort and Merge Sort using random, sorted, reverse-sorted, and repeated-value inputs. I also used the priority queue in a small non-preemptive task scheduler and compared its results with first-in, first-out (FIFO) scheduling.

The scheduler uses fictional infrastructure maintenance tasks. Its durations and deadlines are simulated, not actual work records.

## Project files

| File | Description |
| --- | --- |
| `heapsort.py` | In-place Heapsort using a max-heap |
| `comparison_sorts.py` | Quicksort and Merge Sort implementations |
| `priority_queue.py` | Task model and indexed max-heap |
| `scheduler.py` | Priority and FIFO scheduling |
| `demo.py` | Example sorting and task operations |
| `tests/` | Automated correctness tests |
| `benchmark.py` | Sorting performance comparison |
| `scheduler_experiment.py` | Scheduling experiment |
| `benchmark_results.csv` | Sorting measurements |
| `scheduler_results.csv` | Scheduling summary |
| `scheduler_trace.csv` | Individual task execution results |
| `environment.txt` | Environment used for benchmark measurements |
| `sorting_comparison.png` | Sorting performance charts |
| `Assignment4_Report.docx` | Report and analysis |
| `generate_report.py` | Recreates the report and chart from the results |

## Running the project

Python 3.10 or later is required. From the project folder:

```bash
python3 demo.py
python3 -m unittest discover -s tests -v
```

To run the performance experiments:

```bash
python3 benchmark.py
python3 scheduler_experiment.py
```

The scripts update the CSV files and environment information. To rebuild the chart and report, install the required packages in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python generate_report.py
```

The report and chart are based on the current CSV files. The included benchmark measurements were collected in a Linux environment, as recorded in `environment.txt`. Measurements from another computer may differ.

## Design notes

Heapsort builds a max-heap in linear time and repeatedly moves the maximum element to its final position. Its running time is Θ(n log n), with O(1) auxiliary space for the in-place implementation.

The priority queue uses a Python list as a max-heap and a dictionary mapping task IDs to heap positions. This supports insertion, removal of the highest-priority task, and priority updates in O(log n) worst-case time. Checking whether the queue is empty takes O(1).

Tasks with higher numerical priorities are selected first. Arrival time and insertion order break ties. Once a task starts, it runs to completion.

## Results

In the eight-task scheduling example, priority scheduling reduced average waiting time from 4.875 to 4.625 time units. However, its maximum waiting time was 11 units, compared with 8 units for FIFO. Both approaches missed two deadlines. This shows a trade-off between priority responsiveness and fairness.

Sorting results are recorded in `benchmark_results.csv` and discussed in `Assignment4_Report.docx`. The timings depend on input distribution and the particular implementations tested.
