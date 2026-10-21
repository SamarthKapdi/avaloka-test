import threading
import unittest

from solution import (
    LRUCache,
    ThreadSafeLRUCache,
    assign_specific_rooms,
    can_attend_all,
    min_rooms_required,
)


class LRUCacheTests(unittest.TestCase):
    def test_insertion_and_retrieval(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(cache.get("missing"), -1)

    def test_access_updates_recency(self):
        cache = LRUCache(2)
        cache.put(1, "one")
        cache.put(2, "two")
        cache.get(1)
        cache.put(3, "three")
        self.assertEqual(cache.get(1), "one")
        self.assertEqual(cache.get(2), -1)

    def test_update_changes_value_and_recency_without_eviction(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)
        cache.put("c", 3)
        self.assertEqual(cache.get("a"), 10)
        self.assertEqual(cache.get("b"), -1)

    def test_capacity_one_and_multiple_evictions(self):
        cache = LRUCache(1)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(3), 3)

    def test_zero_capacity_does_not_store(self):
        cache = LRUCache(0)
        cache.put("key", "value")
        self.assertEqual(cache.get("key"), -1)

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            LRUCache(-1)
        with self.assertRaises(ValueError):
            LRUCache(1.5)
        with self.assertRaises(ValueError):
            LRUCache(True)


class SchedulerTests(unittest.TestCase):
    def test_assignment_example(self):
        events = [(9, 10), (10, 11), (11, 12)]
        self.assertTrue(can_attend_all(events))
        self.assertEqual(min_rooms_required(events), 1)

    def test_empty_and_single_event(self):
        self.assertTrue(can_attend_all([]))
        self.assertEqual(min_rooms_required([]), 0)
        self.assertTrue(can_attend_all([(1, 2)]))
        self.assertEqual(min_rooms_required([(1, 2)]), 1)

    def test_unsorted_and_overlapping_events(self):
        events = [(5, 7), (1, 4), (3, 6)]
        self.assertFalse(can_attend_all(events))
        self.assertEqual(min_rooms_required(events), 2)

    def test_identical_and_simultaneous_events(self):
        events = [(1, 4), (1, 4), (1, 4)]
        self.assertFalse(can_attend_all(events))
        self.assertEqual(min_rooms_required(events), 3)

    def test_adjacent_events_reuse_room(self):
        self.assertEqual(min_rooms_required([(1, 2), (2, 3), (3, 4)]), 1)

    def test_invalid_events(self):
        for events in [[(1, 1)], [(2, 1)], [(1,)], [(1, 2, 3)], [("a", 2)]]:
            with self.subTest(events=events):
                with self.assertRaises(ValueError):
                    can_attend_all(events)
                with self.assertRaises(ValueError):
                    min_rooms_required(events)


class ExtensionTests(unittest.TestCase):
    def test_specific_rooms_reuse_and_minimality(self):
        events = [(1, 4), (2, 3), (4, 5), (3, 6)]
        assignments = assign_specific_rooms(events)
        labels = {label for _, label in assignments}
        self.assertEqual(len(labels), min_rooms_required(events))
        self.assertEqual(dict(assignments)[2], "Room A")
        self.assertEqual(dict(assignments)[0], "Room A")

    def test_duplicate_intervals_keep_separate_indices(self):
        assignments = assign_specific_rooms([(1, 3), (1, 3), (3, 4)])
        self.assertEqual([index for index, _ in assignments], [0, 1, 2])
        self.assertEqual(len({label for _, label in assignments}), 2)

    def test_no_overlapping_events_share_room(self):
        events = [(1, 5), (2, 3), (5, 6), (3, 5)]
        assignments = dict(assign_specific_rooms(events))
        for first, (start_a, end_a) in enumerate(events):
            for second in range(first + 1, len(events)):
                start_b, end_b = events[second]
                if start_a < end_b and start_b < end_a:
                    self.assertNotEqual(assignments[first], assignments[second])

    def test_thread_safe_cache_under_concurrent_load(self):
        cache = ThreadSafeLRUCache(100)

        def worker(offset):
            for value in range(offset, offset + 100):
                cache.put(value, value)
                self.assertEqual(cache.get(value), value)

        threads = [threading.Thread(target=worker, args=(offset,)) for offset in range(0, 1000, 100)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(cache._cache), 100)


if __name__ == "__main__":
    unittest.main()
