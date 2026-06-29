"""DDL integrity rules (PRIMARY KEY, FOREIGN KEY, …)."""

from __future__ import annotations


class Constraint:
    """A schema rule: primary key, foreign key, unique, or check."""

    def __init__(
        self,
        kind: str,
        *,
        columns: list[str] | None = None,
        references_table: str | None = None,
        references_columns: list[str] | None = None,
        expression: str | None = None,
    ):
        self.kind = kind
        self.columns = columns or []
        self.references_table = references_table
        self.references_columns = references_columns or []
        self.expression = expression
