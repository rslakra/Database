"""Multi-Version Concurrency Control — snapshot reads without blocking writes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VersionedRecord:
    record_id: str
    versions: list[dict[str, Any]] = field(default_factory=list)
    current: int = 0

    def write(self, body: dict[str, Any]) -> int:
        self.current += 1
        snapshot = {"version": self.current, "body": dict(body)}
        self.versions.append(snapshot)
        return self.current

    def read(self, at_version: int | None = None) -> dict[str, Any] | None:
        if not self.versions:
            return None
        if at_version is None:
            return self.versions[-1]["body"]
        for snap in reversed(self.versions):
            if snap["version"] <= at_version:
                return snap["body"]
        return None


class MVCC:
    """Track versions per record for concurrent SQL and NoSQL access."""

    def __init__(self):
        self._records: dict[str, VersionedRecord] = {}

    def _key(self, namespace_kind: str, namespace: str, record_id: str) -> str:
        return f"{namespace_kind}:{namespace}:{record_id}"

    def write(self, namespace_kind: str, namespace: str, record_id: str, body: dict) -> int:
        key = self._key(namespace_kind, namespace, record_id)
        record = self._records.setdefault(key, VersionedRecord(record_id=record_id))
        return record.write(body)

    def read(
        self,
        namespace_kind: str,
        namespace: str,
        record_id: str,
        at_version: int | None = None,
    ) -> dict | None:
        key = self._key(namespace_kind, namespace, record_id)
        record = self._records.get(key)
        return record.read(at_version) if record else None

    def snapshot_version(self) -> int:
        """Global read snapshot — max version seen across all records."""
        if not self._records:
            return 0
        return max(r.current for r in self._records.values())
