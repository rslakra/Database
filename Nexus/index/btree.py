"""Simple in-memory B+ tree for primary key → storage location mapping."""

from __future__ import annotations

from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class BPlusTree(Generic[K, V]):
    def __init__(self):
        self._store: dict[K, V] = {}

    def insert(self, key: K, value: V) -> None:
        self._store[key] = value

    def lookup(self, key: K) -> V | None:
        return self._store.get(key)

    def delete(self, key: K) -> bool:
        return self._store.pop(key, None) is not None

    def range_scan(self, start: K | None = None, end: K | None = None) -> list[tuple[K, V]]:
        items = sorted(self._store.items(), key=lambda item: item[0])
        result = []
        for key, value in items:
            if start is not None and key < start:
                continue
            if end is not None and key > end:
                break
            result.append((key, value))
        return result
