"""SQL and NoSQL data types supported by Nexus."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Union

TypeInput = Union[str, "SqlDataType"]


class SqlDataType(str, Enum):
    """Relational column types (MySQL-style, one canonical name per kind)."""

    INT = "INT"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    TINYINT = "TINYINT"
    FLOAT = "FLOAT"
    DECIMAL = "DECIMAL"
    VARCHAR = "VARCHAR"
    CHAR = "CHAR"
    TEXT = "TEXT"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"
    BLOB = "BLOB"
    BINARY = "BINARY"


class NoSqlDataType(str, Enum):
    """Document field types (JSON / BSON-style)."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    DATE = "date"
    BINARY = "binary"


@dataclass(frozen=True)
class TypeSpec:
    """Resolved type with optional length/precision from a SQL type string."""

    base: SqlDataType
    length: int | None = None
    precision: int | None = None
    scale: int | None = None
    raw: str = ""

    @property
    def sql_name(self) -> str:
        if self.length is not None and self.base in (SqlDataType.VARCHAR, SqlDataType.CHAR):
            return f"{self.base.value}({self.length})"
        if self.precision is not None and self.base == SqlDataType.DECIMAL:
            if self.scale is not None:
                return f"{self.base.value}({self.precision},{self.scale})"
            return f"{self.base.value}({self.precision})"
        return self.base.value


class TypeValidationError(Exception):
    pass


class DataType:
    """Unified API for SQL and NoSQL type parsing, validation, and coercion."""

    Sql = SqlDataType
    NoSql = NoSqlDataType

    SQL_ALIASES: dict[str, str] = {
        "INTEGER": "INT",
        "BOOL": "BOOLEAN",
        "NUMERIC": "DECIMAL",
        "DOUBLE": "FLOAT",
    }

    NOSQL_COMPAT: dict[NoSqlDataType, frozenset[NoSqlDataType]] = {
        NoSqlDataType.NUMBER: frozenset({NoSqlDataType.INTEGER}),
        NoSqlDataType.STRING: frozenset({NoSqlDataType.DATE}),
    }

    SQL_PYTHON_TYPES: dict[SqlDataType, type] = {
        SqlDataType.INT: int,
        SqlDataType.BIGINT: int,
        SqlDataType.SMALLINT: int,
        SqlDataType.TINYINT: int,
        SqlDataType.FLOAT: float,
        SqlDataType.DECIMAL: Decimal,
        SqlDataType.VARCHAR: str,
        SqlDataType.CHAR: str,
        SqlDataType.TEXT: str,
        SqlDataType.DATE: str,
        SqlDataType.TIME: str,
        SqlDataType.DATETIME: str,
        SqlDataType.TIMESTAMP: str,
        SqlDataType.BOOLEAN: bool,
        SqlDataType.JSON: dict,
        SqlDataType.BLOB: bytes,
        SqlDataType.BINARY: bytes,
    }

    SUPPORTED_SQL_TYPES: tuple[SqlDataType, ...] = tuple(SqlDataType)
    SUPPORTED_NOSQL_TYPES: tuple[NoSqlDataType, ...] = tuple(NoSqlDataType)

    def __init__(
        self,
        type_input: TypeInput,
        *,
        length: int | None = None,
        precision: int | None = None,
        scale: int | None = None,
    ):
        if isinstance(type_input, SqlDataType):
            self._spec = TypeSpec(
                base=type_input,
                length=length,
                precision=precision,
                scale=scale,
                raw=self._format_raw(type_input, length, precision, scale),
            )
        else:
            self._spec = self.parse_sql(str(type_input))

    @property
    def spec(self) -> TypeSpec:
        return self._spec

    @property
    def base(self) -> SqlDataType:
        return self._spec.base

    @property
    def sql_name(self) -> str:
        return self._spec.sql_name

    @property
    def python_type(self) -> type:
        return self.SQL_PYTHON_TYPES[self._spec.base]

    def coerce(self, value: Any) -> Any:
        """Cast a value to this SQL column type."""
        if value is None:
            return None

        base = self._spec.base

        if base in (SqlDataType.INT, SqlDataType.BIGINT, SqlDataType.SMALLINT, SqlDataType.TINYINT):
            return int(value)

        if base == SqlDataType.FLOAT:
            return float(value)

        if base == SqlDataType.DECIMAL:
            return Decimal(str(value))

        if base in (SqlDataType.VARCHAR, SqlDataType.CHAR, SqlDataType.TEXT):
            text = str(value)
            if self._spec.length is not None and len(text) > self._spec.length:
                raise TypeValidationError(
                    f"Value length {len(text)} exceeds {self._spec.sql_name}"
                )
            return text

        if base == SqlDataType.DATE:
            if isinstance(value, date) and not isinstance(value, datetime):
                return value.isoformat()
            return str(value)

        if base in (SqlDataType.TIME, SqlDataType.DATETIME, SqlDataType.TIMESTAMP):
            if isinstance(value, datetime):
                return value.isoformat(sep=" ", timespec="seconds")
            return str(value)

        if base == SqlDataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.strip().lower() in ("1", "true", "yes", "t", "y")
            return bool(value)

        if base == SqlDataType.JSON:
            if isinstance(value, (dict, list)):
                return value
            if isinstance(value, str):
                return json.loads(value)
            raise TypeValidationError(f"Cannot coerce {type(value)} to JSON")

        if base in (SqlDataType.BLOB, SqlDataType.BINARY):
            if isinstance(value, bytes):
                return value
            return str(value).encode("utf-8")

        return value

    def __repr__(self) -> str:
        return f"DataType({self._spec.sql_name!r})"

    @staticmethod
    def _format_raw(
        base: SqlDataType,
        length: int | None,
        precision: int | None,
        scale: int | None,
    ) -> str:
        if length is not None and base in (SqlDataType.VARCHAR, SqlDataType.CHAR):
            return f"{base.value}({length})"
        if precision is not None and base == SqlDataType.DECIMAL:
            if scale is not None:
                return f"{base.value}({precision},{scale})"
            return f"{base.value}({precision})"
        return base.value

    @classmethod
    def _resolve_sql_base(cls, name: str) -> SqlDataType:
        canonical = cls.SQL_ALIASES.get(name, name)
        return SqlDataType(canonical)

    @classmethod
    def parse_sql(cls, type_str: str) -> TypeSpec:
        """Parse 'VARCHAR(20)' or 'INTEGER' (alias for INT) into a TypeSpec."""
        raw = type_str.strip()
        base_name = raw.split("(")[0].upper()
        try:
            base = cls._resolve_sql_base(base_name)
        except ValueError as exc:
            raise TypeValidationError(f"Unsupported SQL type: {type_str}") from exc

        length = precision = scale = None
        if "(" in raw and raw.endswith(")"):
            params = raw[raw.index("(") + 1 : -1]
            parts = [p.strip() for p in params.split(",")]
            if base in (SqlDataType.VARCHAR, SqlDataType.CHAR, SqlDataType.BINARY):
                length = int(parts[0]) if parts[0].isdigit() else None
            elif base == SqlDataType.DECIMAL and parts:
                precision = int(parts[0]) if parts[0].isdigit() else None
                if len(parts) > 1 and parts[1].isdigit():
                    scale = int(parts[1])

        return TypeSpec(base=base, length=length, precision=precision, scale=scale, raw=raw)

    @classmethod
    def sql_type_name(cls, type_str: str) -> str:
        """Return the canonical base SQL type (e.g. 'INT' from 'INTEGER')."""
        return cls.parse_sql(type_str).base.value

    @classmethod
    def is_sql_supported(cls, type_str: str) -> bool:
        try:
            cls.parse_sql(type_str)
            return True
        except TypeValidationError:
            return False

    @classmethod
    def coerce_sql(cls, value: Any, type_str: str) -> Any:
        """Cast a value using a SQL type string without keeping a DataType instance."""
        return cls(type_str).coerce(value)

    @classmethod
    def infer_nosql(cls, value: Any) -> NoSqlDataType:
        """Infer the NoSQL type of a runtime value."""
        if value is None:
            return NoSqlDataType.NULL
        if isinstance(value, bool):
            return NoSqlDataType.BOOLEAN
        if isinstance(value, int) and not isinstance(value, bool):
            return NoSqlDataType.INTEGER
        if isinstance(value, float):
            return NoSqlDataType.NUMBER
        if isinstance(value, str):
            return NoSqlDataType.STRING
        if isinstance(value, list):
            return NoSqlDataType.ARRAY
        if isinstance(value, dict):
            return NoSqlDataType.OBJECT
        if isinstance(value, bytes):
            return NoSqlDataType.BINARY
        if isinstance(value, (date, datetime)):
            return NoSqlDataType.DATE
        return NoSqlDataType.STRING

    @classmethod
    def validate_nosql(cls, value: Any, expected: NoSqlDataType) -> Any:
        """Validate a document field matches an expected NoSQL type."""
        if expected == NoSqlDataType.NULL:
            if value is not None:
                raise TypeValidationError("Expected null")
            return None

        actual = cls.infer_nosql(value)
        compatible = cls.NOSQL_COMPAT.get(expected, frozenset())
        if actual != expected and actual not in compatible:
            raise TypeValidationError(f"Expected {expected.value}, got {actual.value}")
        return value


# Module-level aliases (backward compatible)
parse_sql_type = DataType.parse_sql
sql_type_name = DataType.sql_type_name
is_sql_type_supported = DataType.is_sql_supported
coerce_sql_value = DataType.coerce_sql
infer_nosql_type = DataType.infer_nosql
validate_nosql_value = DataType.validate_nosql
SQL_TYPE_ALIASES = DataType.SQL_ALIASES
SQL_PYTHON_TYPES = DataType.SQL_PYTHON_TYPES
SUPPORTED_SQL_TYPES = DataType.SUPPORTED_SQL_TYPES
SUPPORTED_NOSQL_TYPES = DataType.SUPPORTED_NOSQL_TYPES
