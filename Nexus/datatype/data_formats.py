"""File format enums and row aliases for connectors."""

from __future__ import annotations

from enum import Enum
from typing import Any, TypeAlias

RowDict: TypeAlias = dict[str, Any]
RowList: TypeAlias = list[RowDict]


class DataFormat(str, Enum):
    """Supported connector formats for import and export."""

    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    EXCEL = "excel"
