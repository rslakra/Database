"""Data connector protocol for file import and export."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from datatype.data_formats import RowDict, RowList


class ConnectorError(Exception):
    """Raised when a connector cannot read or write a file."""


class DataConnector(ABC):
    """Read and write tabular or document rows to/from external files."""

    format_name: str
    file_extensions: tuple[str, ...]

    @abstractmethod
    def read(self, path: str | Path, **options: Any) -> RowList:
        """Load rows from a file. Each row is a dict of field → value."""

    @abstractmethod
    def write(self, path: str | Path, rows: RowList, **options: Any) -> None:
        """Persist rows to a file."""

    def supports(self, path: str | Path) -> bool:
        suffix = Path(path).suffix.lower().lstrip(".")
        return suffix in self.file_extensions
