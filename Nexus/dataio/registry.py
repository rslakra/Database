"""Connector registry — resolve format name or file extension to a connector."""

from __future__ import annotations

from pathlib import Path

from dataio.base import ConnectorError, DataConnector
from dataio.csv_connector import CSVConnector
from dataio.excel_connector import ExcelConnector
from dataio.json_connector import JSONConnector, JSONLConnector
from datatype.data_formats import DataFormat

_BUILTIN_CONNECTORS: list[DataConnector] = [
    CSVConnector(),
    JSONConnector(),
    JSONLConnector(),
    ExcelConnector(),
]

_BY_FORMAT: dict[str, DataConnector] = {c.format_name: c for c in _BUILTIN_CONNECTORS}
_BY_EXTENSION: dict[str, DataConnector] = {}
for connector in _BUILTIN_CONNECTORS:
    for ext in connector.file_extensions:
        _BY_EXTENSION[ext] = connector


def get_connector(fmt: str | DataFormat) -> DataConnector:
    """Return a connector by format name (csv, json, jsonl, excel)."""
    key = fmt.value if isinstance(fmt, DataFormat) else fmt.lower()
    connector = _BY_FORMAT.get(key)
    if connector is None:
        raise ConnectorError(f"Unknown format: {fmt}. Supported: {list(_BY_FORMAT)}")
    return connector


def get_connector_for_path(path: str | Path) -> DataConnector:
    """Pick a connector from the file extension."""
    ext = Path(path).suffix.lower().lstrip(".")
    connector = _BY_EXTENSION.get(ext)
    if connector is None:
        raise ConnectorError(
            f"No connector for '.{ext}'. Supported extensions: {list(_BY_EXTENSION)}"
        )
    return connector


def register_connector(connector: DataConnector) -> None:
    """Plug in a custom connector at runtime."""
    _BUILTIN_CONNECTORS.append(connector)
    _BY_FORMAT[connector.format_name] = connector
    for ext in connector.file_extensions:
        _BY_EXTENSION[ext] = connector
