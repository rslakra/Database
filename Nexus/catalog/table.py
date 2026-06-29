"""DDL table definition."""

from __future__ import annotations

from catalog.column import Column
from catalog.constraint import Constraint
from catalog.index import IndexMeta


class Table:
    """Named collection of columns and rules; rows are Row instances."""

    def __init__(
        self,
        name: str,
        *,
        columns: list[Column] | None = None,
        attributes: list[Column] | None = None,
        constraints: list[Constraint] | None = None,
        indexes: list[IndexMeta] | None = None,
    ):
        self.name = name
        self.columns = columns if columns is not None else (attributes or [])
        self.constraints = constraints or []
        self.indexes = indexes or []

    @property
    def attributes(self) -> list[Column]:
        """Backward-compatible alias for ``columns``."""
        return self.columns
