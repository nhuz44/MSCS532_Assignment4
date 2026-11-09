"""Manual array-based max-heap priority queue with indexed key updates."""
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class Task:
    """A fictional task for a non-preemptive infrastructure job scheduler."""

    task_id: str
    priority: int
    arrival_time: int
    duration: int
    deadline: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a nonempty string")
        for name in ("priority", "arrival_time", "duration"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer")
        if self.priority < 0 or self.arrival_time < 0 or self.duration < 1:
            raise ValueError("priority and arrival must be >=0; duration must be >0")
        if self.deadline is not None:
            if type(self.deadline) is not int:
                raise TypeError("deadline must be an integer or None")
            if self.deadline < self.arrival_time:
                raise ValueError("deadline cannot precede arrival")


class MaxPriorityQueue:
    """Max heap: highest priority first, then earlier arrival, then FIFO.

    An index map provides O(1) access to a task's heap position; insertion,
    extraction, and updating a priority take O(log n) worst case.
    """

    def __init__(self) -> None:
        self._heap: list[tuple[Task, int]] = []
        self._positions: dict[str, int] = {}
        self._sequence = 0

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return not self._heap

    @staticmethod
    def _rank(entry: tuple[Task, int]) -> tuple[int, int, int]:
        task, sequence = entry
        return task.priority, -task.arrival_time, -sequence

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._positions[self._heap[i][0].task_id] = i
        self._positions[self._heap[j][0].task_id] = j

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._rank(self._heap[parent]) >= self._rank(self._heap[i]):
                break
            self._swap(i, parent)
            i = parent

    def _sift_down(self, i: int) -> None:
        n = len(self._heap)
        while 2 * i + 1 < n:
            left = 2 * i + 1
            right = left + 1
            best = left
            if right < n and self._rank(self._heap[right]) > self._rank(self._heap[left]):
                best = right
            if self._rank(self._heap[i]) >= self._rank(self._heap[best]):
                break
            self._swap(i, best)
            i = best

    def insert(self, task: Task) -> None:
        if task.task_id in self._positions:
            raise ValueError(f"duplicate task_id: {task.task_id}")
        self._positions[task.task_id] = len(self._heap)
        self._heap.append((task, self._sequence))
        self._sequence += 1
        self._sift_up(len(self._heap) - 1)

    def peek(self) -> Task:
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        return self._heap[0][0]

    def extract_max(self) -> Task:
        if not self._heap:
            raise IndexError("extract from empty priority queue")
        best = self._heap[0][0]
        last = self._heap.pop()
        del self._positions[best.task_id]
        if self._heap:
            self._heap[0] = last
            self._positions[last[0].task_id] = 0
            self._sift_down(0)
        return best

    def get(self, task_id: str) -> Task:
        if task_id not in self._positions:
            raise KeyError(task_id)
        return self._heap[self._positions[task_id]][0]

    def change_priority(self, task_id: str, new_priority: int) -> Task:
        if type(new_priority) is not int or new_priority < 0:
            raise ValueError("new_priority must be a nonnegative integer")
        i = self._positions[task_id]  # KeyError for unknown tasks.
        task, sequence = self._heap[i]
        updated = replace(task, priority=new_priority)
        self._heap[i] = (updated, sequence)
        if new_priority > task.priority:
            self._sift_up(i)
        elif new_priority < task.priority:
            self._sift_down(i)
        return updated

    def increase_key(self, task_id: str, new_priority: int) -> Task:
        if new_priority <= self.get(task_id).priority:
            raise ValueError("increase_key must increase the priority")
        return self.change_priority(task_id, new_priority)

    def decrease_key(self, task_id: str, new_priority: int) -> Task:
        if new_priority >= self.get(task_id).priority:
            raise ValueError("decrease_key must decrease the priority")
        return self.change_priority(task_id, new_priority)

    def validate_heap(self) -> bool:
        """For unit tests: verify parent invariant and index-map consistency."""
        if len(self._positions) != len(self._heap):
            return False
        for i, entry in enumerate(self._heap):
            if self._positions.get(entry[0].task_id) != i:
                return False
            for child in (2 * i + 1, 2 * i + 2):
                if child < len(self._heap) and self._rank(entry) < self._rank(self._heap[child]):
                    return False
        return True
