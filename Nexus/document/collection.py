"""Document collection namespace."""

from __future__ import annotations

from enum import Enum


class SchemaMode(str, Enum):
    SCHEMALESS = "schemaless"
    STRICT = "strict"


class Collection:
    def __init__(
        self,
        name: str,
        *,
        mode: SchemaMode = SchemaMode.SCHEMALESS,
        required_fields: list[str] | None = None,
    ):
        self.name = name
        self.mode = mode
        self.required_fields = required_fields or []
