"""Logical namespaces — separate SQL tables from NoSQL collections on one engine."""

from __future__ import annotations

from enum import Enum


class NamespaceKind(str, Enum):
    TABLE = "table"
    COLLECTION = "collection"


def storage_key(kind: NamespaceKind, name: str, record_id: str) -> str:
    """Build a unified key-value key: kind/name/id."""
    return f"{kind.value}:{name}:{record_id}"
