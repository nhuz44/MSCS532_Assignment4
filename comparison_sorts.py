"""Hand-written sorting algorithms for comparison with Heapsort."""
from random import Random
from typing import MutableSequence, TypeVar

T = TypeVar("T")


def quick_sort(values: MutableSequence[T], *, seed: int = 2026) -> MutableSequence[T]:
    """Random-pivot, three-way in-place Quicksort with an explicit stack.

    Expected O(n log n); worst-case O(n^2). Equal values are partitioned
    together to avoid redundant work on duplicate-heavy inputs.
    """
    random = Random(seed)
    stack = [(0, len(values) - 1)]
    while stack:
        lo, hi = stack.pop()
        while lo < hi:
            pivot = values[random.randint(lo, hi)]
            lt, i, gt = lo, lo, hi
            while i <= gt:
                if values[i] < pivot:
                    values[lt], values[i] = values[i], values[lt]
                    lt += 1
                    i += 1
                elif values[i] > pivot:
                    values[gt], values[i] = values[i], values[gt]
                    gt -= 1
                else:
                    i += 1
            # Process smaller partition immediately to limit explicit stack.
            left_length, right_length = lt - lo, hi - gt
            if left_length < right_length:
                if gt + 1 < hi:
                    stack.append((gt + 1, hi))
                hi = lt - 1
            else:
                if lo < lt - 1:
                    stack.append((lo, lt - 1))
                lo = gt + 1
    return values


def merge_sort(values: MutableSequence[T]) -> MutableSequence[T]:
    """Stable, bottom-up Merge Sort; O(n log n) time and O(n) space."""
    n = len(values)
    if n < 2:
        return values
    source = list(values)
    dest = [None] * n
    width = 1
    while width < n:
        for start in range(0, n, 2 * width):
            middle = min(start + width, n)
            end = min(start + 2 * width, n)
            i, j, k = start, middle, start
            while i < middle and j < end:
                if source[i] <= source[j]:
                    dest[k] = source[i]
                    i += 1
                else:
                    dest[k] = source[j]
                    j += 1
                k += 1
            while i < middle:
                dest[k] = source[i]
                i += 1
                k += 1
            while j < end:
                dest[k] = source[j]
                j += 1
                k += 1
        source, dest = dest, source
        width *= 2
    values[:] = source
    return values
