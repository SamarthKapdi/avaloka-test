"""Implementations for the Avaloka AI Intern take-home assignment."""

from __future__ import annotations

import heapq
import threading
from numbers import Real
from typing import Any, Hashable, Iterable, List, Optional, Sequence, Tuple


class _Node:
    """A node in the LRU cache's doubly linked list."""

    def __init__(self, key: Hashable = None, value: Any = None) -> None:
        self.key = key
        self.value = value
        self.prev: Optional[_Node] = None
        self.next: Optional[_Node] = None


class LRUCache:
    """An O(1)-average LRU cache backed by a dictionary and linked list."""

    def __init__(self, capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise ValueError("capacity must be a non-negative integer")
        if capacity < 0:
            raise ValueError("capacity must be a non-negative integer")

        self.capacity = capacity
        self._cache: dict[Hashable, _Node] = {}
        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node: _Node) -> None:
        previous = node.prev
        following = node.next
        if previous is None or following is None:
            raise RuntimeError("cannot remove a detached cache node")
        previous.next = following
        following.prev = previous

    def _add_to_front(self, node: _Node) -> None:
        following = self._head.next
        if following is None:
            raise RuntimeError("cache list is not initialized")
        node.prev = self._head
        node.next = following
        self._head.next = node
        following.prev = node

    def _move_to_front(self, node: _Node) -> None:
        self._remove(node)
        self._add_to_front(node)

    def get(self, key: Hashable) -> Any:
        node = self._cache.get(key)
        if node is None:
            return -1
        self._move_to_front(node)
        return node.value

    def put(self, key: Hashable, value: Any) -> None:
        if self.capacity == 0:
            return

        existing = self._cache.get(key)
        if existing is not None:
            existing.value = value
            self._move_to_front(existing)
            return

        node = _Node(key, value)
        self._cache[key] = node
        self._add_to_front(node)

        if len(self._cache) > self.capacity:
            least_recent = self._tail.prev
            if least_recent is None or least_recent is self._head:
                raise RuntimeError("cache list is inconsistent")
            self._remove(least_recent)
            del self._cache[least_recent.key]


class ThreadSafeLRUCache(LRUCache):
    """An LRU cache whose complete operations are protected by an RLock."""

    def __init__(self, capacity: int) -> None:
        super().__init__(capacity)
        self._lock = threading.RLock()

    def get(self, key: Hashable) -> Any:
        with self._lock:
            # get changes recency, so it must be synchronized like put.
            return super().get(key)

    def put(self, key: Hashable, value: Any) -> None:
        with self._lock:
            super().put(key, value)


Event = Tuple[Real, Real]


def _validated_events(events: Iterable[Sequence[Real]]) -> List[Event]:
    """Validate and materialize event input for the scheduling functions."""
    try:
        materialized = list(events)
    except TypeError as error:
        raise ValueError("events must be an iterable of two-number events") from error

    validated: List[Event] = []
    for event in materialized:
        if isinstance(event, (str, bytes)) or not isinstance(event, Sequence):
            raise ValueError("each event must contain exactly two numeric times")
        if len(event) != 2:
            raise ValueError("each event must contain exactly two numeric times")
        start, end = event
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, Real)
            or not isinstance(end, Real)
        ):
            raise ValueError("event times must be numeric")
        if not start < end:
            raise ValueError("event start_time must be less than end_time")
        validated.append((start, end))
    return validated


def can_attend_all(events: Iterable[Sequence[Real]]) -> bool:
    """Return whether all events can be attended by one person."""
    ordered = sorted(_validated_events(events), key=lambda event: event[0])
    return all(previous[1] <= current[0] for previous, current in zip(ordered, ordered[1:]))


def min_rooms_required(events: Iterable[Sequence[Real]]) -> int:
    """Return the minimum number of rooms needed for all events."""
    ordered = sorted(_validated_events(events), key=lambda event: event[0])
    occupied: List[Real] = []
    maximum = 0
    for start, end in ordered:
        while occupied and occupied[0] <= start:
            heapq.heappop(occupied)
        heapq.heappush(occupied, end)
        maximum = max(maximum, len(occupied))
    return maximum


def _room_label(number: int) -> str:
    """Convert a zero-based room number into a readable spreadsheet-style label."""
    label = ""
    number += 1
    while number:
        number, remainder = divmod(number - 1, 26)
        label = chr(ord("A") + remainder) + label
    return f"Room {label}"


def assign_specific_rooms(events: Iterable[Sequence[Real]]) -> List[Tuple[int, str]]:
    """Assign every original event index to a minimum set of reusable room labels."""
    validated = _validated_events(events)
    ordered = sorted(
        enumerate(validated), key=lambda item: (item[1][0], item[1][1], item[0])
    )
    occupied: List[Tuple[Real, int]] = []
    available: List[int] = []
    assignments: List[Optional[Tuple[int, str]]] = [None] * len(validated)
    next_room = 0

    for index, (start, end) in ordered:
        while occupied and occupied[0][0] <= start:
            _, room = heapq.heappop(occupied)
            heapq.heappush(available, room)
        if available:
            room = heapq.heappop(available)
        else:
            room = next_room
            next_room += 1
        assignments[index] = (index, _room_label(room))
        heapq.heappush(occupied, (end, room))

    return [assignment for assignment in assignments if assignment is not None]
