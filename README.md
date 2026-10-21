# Avaloka DSA Systems Assignment

## Overview

This Python 3, standard-library-only solution implements an LRU cache, meeting
scheduling algorithms, reusable room assignments, and a thread-safe cache
extension.

## Requirements and usage

Python 3.9 or newer is recommended. Run the complete test suite from the
project root:

```text
python -m unittest discover -s tests -v
```

Example:

```python
from solution import LRUCache, assign_specific_rooms, can_attend_all, min_rooms_required

cache = LRUCache(2)
cache.put("user", "Ada")
cache.get("user")                         # "Ada"

events = [(9, 10), (10, 11), (11, 12)]
can_attend_all(events)                    # True
min_rooms_required(events)                # 1
assign_specific_rooms([(1, 3), (1, 2), (3, 4)])
# [(0, "Room A"), (1, "Room B"), (2, "Room A")]
```

Events must be two-item sequences of numeric values with `start_time <
end_time`. Invalid events raise `ValueError`. Room assignments are returned as
`(original_index, room_label)` pairs, so duplicate event tuples remain
distinct.

## Data structures and algorithms

### LRU cache

`LRUCache` combines a dictionary from keys to nodes with a manually
implemented doubly linked list. Dummy head and tail nodes make insertion,
removal, and movement uniform: the newest entry is after the head and the
oldest is before the tail. The private `_remove`, `_add_to_front`, and
`_move_to_front` helpers keep pointer manipulation localized.

Dictionary lookup plus linked-list updates make `get` and `put` **O(1)
average time** and **O(capacity) space**. The trade-off is a little more
memory and pointer bookkeeping than a simple dictionary, in exchange for
constant-time recency ordering. `OrderedDict` and `functools.lru_cache` are
intentionally not used.

### Event scheduling

`can_attend_all` sorts a copy by start time and compares adjacent intervals.
It is **O(n log n) time** and **O(n) space**. `min_rooms_required` sorts first,
then uses a `heapq` min-heap of active end times. End times at or before the
next start are popped before the new end is pushed. The heap size is the
number of simultaneously occupied rooms, so its maximum is the minimum
possible room count: every event in that simultaneous set needs a different
room, and freed rooms are immediately reused. Its complexity is **O(n log n)
time** and **O(n) space**.

### Specific room assignment

`assign_specific_rooms` retains each original index while sorting by start
time. One min-heap stores `(end_time, room_number)` for occupied rooms and a
second stores reusable room numbers. Rooms are released before each event,
available identifiers are reused first, and a new identifier is created only
when necessary. This is **O(n log n) time** and **O(n) space**, and uses the
same minimum number of rooms as `min_rooms_required`.

### Thread safety

`ThreadSafeLRUCache` extends the primary cache and protects each complete
`get` and `put` with one `threading.RLock`. `get` needs the lock because it
changes recency by moving a node, not merely reading a value. The Python GIL
does not make this multi-step dictionary/list invariant safe; explicit locking
does.

## Files

- `solution.py`: all implementations.
- `tests/test_solution.py`: `unittest` coverage for normal behavior, edge
  cases, scheduling, room assignment, and concurrent cache use.
- `.gitignore`: Python bytecode, environments, and local development files.
