"""In-place ascending Heapsort using an array-backed binary max-heap.

This is a manual heap implementation, not a wrapper around heapq/sorted().
"""
from typing import MutableSequence, TypeVar

T = TypeVar("T")


def _sift_down(values: MutableSequence[T], root: int, size: int) -> None:
    """Restore the max-heap invariant within values[:size] from root."""
    while True:
        left = 2 * root + 1
        if left >= size:
            return
        right = left + 1
        largest = left
        if right < size and values[right] > values[left]:
            largest = right
        if values[root] >= values[largest]:
            return
        values[root], values[largest] = values[largest], values[root]
        root = largest


def heap_sort(values: MutableSequence[T]) -> MutableSequence[T]:
    """Sort values in ascending order, in place, and return the same sequence.

    Construction is O(n); n extractions are O(log n) each.
    Time: Theta(n log n) for this conventional algorithm (nontrivial n).
    Auxiliary space: O(1). Sorting is not stable.
    """
    size = len(values)
    # Build the max-heap by sifting each internal node toward the bottom.
    for parent in range(size // 2 - 1, -1, -1):
        _sift_down(values, parent, size)

    # Move each maximum to the end of the shrinking heap.
    for end in range(size - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        _sift_down(values, 0, end)
    return values


if __name__ == "__main__":
    sample = [12, 5, 9, 2, 18, 7, 7]
    print("Original:", sample)
    heap_sort(sample)
    print("Heapsort:", sample)
