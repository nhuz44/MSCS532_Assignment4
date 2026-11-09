import random
import unittest
from heapsort import heap_sort
from comparison_sorts import quick_sort, merge_sort


class TestSorting(unittest.TestCase):
    def test_empty(self):
        for sorter in (heap_sort, quick_sort, merge_sort):
            self.assertEqual(sorter([]), [])

    def test_single(self):
        for sorter in (heap_sort, quick_sort, merge_sort):
            self.assertEqual(sorter([8]), [8])

    def test_sorted(self):
        for sorter in (heap_sort, quick_sort, merge_sort):
            self.assertEqual(sorter(list(range(50))), list(range(50)))

    def test_reverse(self):
        for sorter in (heap_sort, quick_sort, merge_sort):
            self.assertEqual(sorter(list(range(50, -1, -1))), list(range(51)))

    def test_duplicates(self):
        for sorter in (heap_sort, quick_sort, merge_sort):
            self.assertEqual(sorter([4, 7, 4, 1, 1, 9]), [1, 1, 4, 4, 7, 9])

    def test_negative_and_float(self):
        for sorter in (heap_sort, quick_sort, merge_sort):
            self.assertEqual(sorter([-4, 2.5, 0, -1.2]), [-4, -1.2, 0, 2.5])

    def test_random_1000(self):
        rng = random.Random(2042)
        numbers = [rng.randint(-10000, 10000) for _ in range(1000)]
        for sorter in (heap_sort, quick_sort, merge_sort):
            self.assertEqual(sorter(numbers.copy()), sorted(numbers))

    def test_heapsort_returns_same_list(self):
        data = [3, 1, 2]
        self.assertIs(heap_sort(data), data)


if __name__ == '__main__':
    unittest.main()
