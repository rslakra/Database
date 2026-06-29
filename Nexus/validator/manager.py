"""Write validation — strict SQL rows vs schemaless documents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from datatype.data_types import DataType, TypeValidationError
from document.collection import Collection, SchemaMode

if TYPE_CHECKING:
    from catalog.table import Table


class ValidationError(Exception):
    pass


class Validator:
    def __init__(self):
        self.tables: dict[str, "Table"] = {}
        self.collections: dict[str, Collection] = {}

    def register_table(self, table: "Table") -> None:
        self.tables[table.name] = table

    def register_collection(self, collection: Collection) -> None:
        self.collections[collection.name] = collection

    def validate_row(self, table_name: str, values: dict[str, Any]) -> dict[str, Any]:
        table = self.tables.get(table_name)
        if table is None:
            raise ValidationError(f"Unknown table: {table_name}")

        normalized: dict[str, Any] = {}
        for col in table.columns:
            if col.name in values:
                val = values[col.name]
            elif col.default is not None:
                val = col.default
            elif not col.nullable and not col.auto_increment:
                raise ValidationError(f"Missing required column: {col.name}")
            else:
                continue

            if val is None and not col.nullable:
                raise ValidationError(f"NULL not allowed for column: {col.name}")

            try:
                normalized[col.name] = DataType(col.type_sql).coerce(val)
            except TypeValidationError as exc:
                raise ValidationError(f"Column '{col.name}': {exc}") from exc

        return normalized

    def validate_document(self, collection_name: str, data: dict[str, Any]) -> dict[str, Any]:
        collection = self.collections.get(collection_name)
        if collection is None:
            raise ValidationError(f"Unknown collection: {collection_name}")

        if collection.mode == SchemaMode.SCHEMALESS:
            return dict(data)

        for field in collection.required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        return dict(data)


# Backward-compatible aliases
SchemaManager = Validator
SchemaValidationError = ValidationError
