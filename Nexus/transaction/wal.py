"""Write-Ahead Log — every write is logged before applying to storage."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class WalOp(str, Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class WalEntry:
    seq: int
    timestamp: str
    op: WalOp
    namespace_kind: str
    namespace: str
    record_id: str
    payload: dict[str, Any]


class WriteAheadLog:
    """Append-only log for crash recovery."""

    def __init__(self, log_path: Path | None = None):
        self.log_path = log_path
        self._entries: list[WalEntry] = []
        self._seq = 0

    def append(
        self,
        op: WalOp,
        *,
        namespace_kind: str,
        namespace: str,
        record_id: str,
        payload: dict[str, Any],
    ) -> WalEntry:
        self._seq += 1
        entry = WalEntry(
            seq=self._seq,
            timestamp=datetime.now(timezone.utc).isoformat(),
            op=op,
            namespace_kind=namespace_kind,
            namespace=namespace,
            record_id=record_id,
            payload=payload,
        )
        self._entries.append(entry)
        if self.log_path:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(asdict(entry), default=str) + "\n")
        return entry

    def replay(self) -> list[WalEntry]:
        if self.log_path and self.log_path.exists():
            lines = self.log_path.read_text(encoding="utf-8").strip().splitlines()
            return [WalEntry(**json.loads(line)) for line in lines if line]
        return list(self._entries)
