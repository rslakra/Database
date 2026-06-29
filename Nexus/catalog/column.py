"""SQL column definition (CREATE TABLE)."""

from __future__ import annotations

from typing import Union

from datatype.data_types import DataType, SqlDataType

TypeInput = Union[str, SqlDataType]


class Column:
    """One column in a table schema."""

    def __init__(
        self,
        name: str,
        data_type: TypeInput,
        *,
        nullable: bool = True,
        default=None,
        auto_increment: bool = False,
        length: int | None = None,
    ):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.default = default
        self.auto_increment = auto_increment
        self.length = length
        self.type_sql = self._resolve_sql_type(data_type, length)

        if not DataType.is_sql_supported(self.type_sql):
            raise ValueError(f"Unsupported data type: {self.type_sql}")

    @staticmethod
    def _resolve_sql_type(data_type: TypeInput, length: int | None) -> str:
        if isinstance(data_type, SqlDataType):
            if length is not None and data_type in (SqlDataType.VARCHAR, SqlDataType.CHAR):
                return f"{data_type.value}({length})"
            return data_type.value
        return str(data_type)

    def __repr__(self) -> str:
        return f"Column({self.name!r}, {self.type_sql!r})"


# Backward-compatible alias
Attribute = Column
