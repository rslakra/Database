"""DDL index metadata (CREATE INDEX) — not the runtime index engine."""

from __future__ import annotations


class IndexMeta:
    """Secondary index definition on a table."""

    def __init__(
        self,
        name: str,
        *,
        table_name: str,
        columns: list[str],
        unique: bool = False,
    ):
        self.name = name
        self.table_name = table_name
        self.columns = columns
        self.unique = unique


# Backward-compatible alias
Index = IndexMeta
