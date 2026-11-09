import random
import unittest
from priority_queue import Task, MaxPriorityQueue


def task(tid, priority, arrival=0):
    return Task(tid, priority, arrival, 1)


class TestPriorityQueue(unittest.TestCase):
    def test_empty(self):
        queue = MaxPriorityQueue()
        self.assertTrue(queue.is_empty())
        self.assertEqual(len(queue), 0)
        with self.assertRaises(IndexError):
            queue.peek()
        with self.assertRaises(IndexError):
            queue.extract_max()

    def test_insert_and_extract(self):
        queue = MaxPriorityQueue()
        for t in (task('a', 3), task('b', 9), task('c', 6)):
            queue.insert(t)
        self.assertEqual(queue.peek().task_id, 'b')
        self.assertEqual([queue.extract_max().task_id for _ in range(3)], ['b', 'c', 'a'])
        self.assertTrue(queue.is_empty())

    def test_ties_fifo(self):
        queue = MaxPriorityQueue()
        for t in (task('a', 3, 0), task('b', 3, 1), task('c', 3, 1)):
            queue.insert(t)
        self.assertEqual([queue.extract_max().task_id for _ in range(3)], ['a', 'b', 'c'])

    def test_increase_key(self):
        queue = MaxPriorityQueue()
        for t in (task('a', 1), task('b', 5), task('c', 3)):
            queue.insert(t)
        queue.increase_key('a', 10)
        self.assertTrue(queue.validate_heap())
        self.assertEqual(queue.extract_max().task_id, 'a')

    def test_decrease_key(self):
        queue = MaxPriorityQueue()
        for t in (task('a', 10), task('b', 5), task('c', 3)):
            queue.insert(t)
        queue.decrease_key('a', 0)
        self.assertTrue(queue.validate_heap())
        self.assertEqual([queue.extract_max().task_id for _ in range(3)], ['b', 'c', 'a'])

    def test_change_priority_both_directions(self):
        queue = MaxPriorityQueue()
        for i, p in enumerate([7, 2, 10, 4, 9, 6]):
            queue.insert(task(str(i), p))
        queue.change_priority('2', 1)
        queue.change_priority('1', 11)
        self.assertTrue(queue.validate_heap())
        self.assertEqual([queue.extract_max().priority for _ in range(6)], [11, 9, 7, 6, 4, 1])

    def test_duplicate_id(self):
        queue = MaxPriorityQueue()
        queue.insert(task('a', 1))
        with self.assertRaises(ValueError):
            queue.insert(task('a', 2))

    def test_unknown_id(self):
        queue = MaxPriorityQueue()
        with self.assertRaises(KeyError):
            queue.change_priority('not-here', 3)

    def test_invalid_key_direction(self):
        queue = MaxPriorityQueue()
        queue.insert(task('a', 3))
        with self.assertRaises(ValueError):
            queue.increase_key('a', 2)
        with self.assertRaises(ValueError):
            queue.decrease_key('a', 3)
        with self.assertRaises(ValueError):
            queue.change_priority('a', -5)

    def test_invalid_task(self):
        for kwargs in ({'task_id':'','priority':2,'arrival_time':0,'duration':1},
                       {'task_id':'x','priority':-1,'arrival_time':0,'duration':1},
                       {'task_id':'x','priority':2,'arrival_time':0,'duration':0},
                       {'task_id':'x','priority':2,'arrival_time':3,'duration':1,'deadline':2}):
            with self.assertRaises(ValueError):
                Task(**kwargs)

    def test_random_operations_invariant(self):
        queue = MaxPriorityQueue()
        rng = random.Random(99)
        ids = {}
        for i in range(100):
            prio = rng.randrange(20)
            queue.insert(task(f't-{i}', prio))
            ids[f't-{i}'] = prio
            self.assertTrue(queue.validate_heap())
        for i in range(75):
            key = f't-{rng.randrange(100)}'
            prio = rng.randrange(30)
            queue.change_priority(key, prio)
            ids[key] = prio
            self.assertTrue(queue.validate_heap())
        result = [queue.extract_max().priority for _ in range(100)]
        self.assertEqual(result, sorted(ids.values(), reverse=True))


if __name__ == '__main__':
    unittest.main()
