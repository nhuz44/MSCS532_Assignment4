import unittest
from priority_queue import Task
from scheduler import schedule, sample_tasks, metrics


class TestScheduler(unittest.TestCase):
    def test_sample_all_tasks_once(self):
        tasks = sample_tasks()
        runs = schedule(tasks)
        self.assertEqual({x.task_id for x in runs}, {t.task_id for t in tasks})
        self.assertEqual(len(runs), len(tasks))

    def test_never_before_arrival(self):
        for run in schedule(sample_tasks()):
            self.assertGreaterEqual(run.start_time, run.arrival_time)

    def test_priority_over_fifo(self):
        jobs = [Task('low', 1, 0, 3, 20), Task('high', 10, 0, 1, 5)]
        self.assertEqual(schedule(jobs, policy='priority')[0].task_id, 'high')
        self.assertEqual(schedule(jobs, policy='fifo')[0].task_id, 'low')

    def test_idle_until_next_arrival(self):
        runs = schedule([Task('late', 5, 10, 2, 12)])
        self.assertEqual((runs[0].start_time, runs[0].end_time), (10, 12))

    def test_no_preemption(self):
        jobs = [Task('long', 2, 0, 10, 25), Task('urgent', 9, 1, 1, 25)]
        self.assertEqual([x.task_id for x in schedule(jobs)], ['long', 'urgent'])

    def test_empty(self):
        self.assertEqual(schedule([]), [])
        self.assertEqual(metrics([])['average_wait'], 0)

    def test_duplicate_task_id(self):
        with self.assertRaises(ValueError):
            schedule([Task('x', 1, 0, 1), Task('x', 2, 0, 1)])

    def test_bad_policy(self):
        with self.assertRaises(ValueError):
            schedule([], policy='undefined')

    def test_metrics(self):
        tasks = [Task('a', 8, 0, 2, 1), Task('b', 1, 0, 1, 5)]
        m = metrics(schedule(tasks))
        self.assertEqual(m['tasks'], 2)
        self.assertEqual(m['deadline_misses'], 1)
        self.assertAlmostEqual(m['average_wait'], 1)


if __name__ == '__main__':
    unittest.main()
