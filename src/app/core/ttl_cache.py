"""Tiny in-process TTLCache used to memoize the current user lookup.

Avoids hitting the database on every authenticated request. Entries
expire after ``ttl_seconds`` and the cache is bounded by ``maxsize``.
"""

import time
from collections import OrderedDict
from threading import Lock
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Thread-safe LRU cache with per-entry TTL expiration."""

    def __init__(self, maxsize: int = 1024, ttl_seconds: float = 30.0) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be > 0")
        self.maxsize = maxsize
        self.ttl = ttl_seconds
        self._data: "OrderedDict[str, tuple[float, T]]" = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> T | None:
        now = time.monotonic()
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < now:
                self._data.pop(key, None)
                return None
            self._data.move_to_end(key)
            return value

    def set(self, key: str, value: T) -> None:
        now = time.monotonic()
        expires_at = now + self.ttl
        with self._lock:
            self._data[key] = (expires_at, value)
            self._data.move_to_end(key)
            while len(self._data) > self.maxsize:
                self._data.popitem(last=False)

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)
