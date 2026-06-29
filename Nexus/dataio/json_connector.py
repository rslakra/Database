"""JSON and JSONL file connectors — stdlib only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dataio.base import ConnectorError, DataConnector
from datatype.data_formats import RowList


class JSONConnector(DataConnector):
    format_name = "json"
    file_extensions = ("json",)

    def read(self, path: str | Path, **options: Any) -> RowList:
        path = Path(path)
        if not path.exists():
            raise ConnectorError(f"File not found: {path}")

        encoding = options.get("encoding", "utf-8")
        root_key = options.get("root_key")

        with path.open(encoding=encoding) as fh:
            payload = json.load(fh)

        if root_key:
            payload = payload.get(root_key, [])
        if isinstance(payload, dict):
            return [payload]
        if not isinstance(payload, list):
            raise ConnectorError("JSON root must be an object or array of objects")
        return [row for row in payload if isinstance(row, dict)]

    def write(self, path: str | Path, rows: RowList, **options: Any) -> None:
        path = Path(path)
        encoding = options.get("encoding", "utf-8")
        indent = options.get("indent", 2)
        root_key = options.get("root_key")

        payload: Any = {root_key: rows} if root_key else rows
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding=encoding) as fh:
            json.dump(payload, fh, indent=indent, default=str)


class JSONLConnector(DataConnector):
    """Newline-delimited JSON — one document per line."""

    format_name = "jsonl"
    file_extensions = ("jsonl", "ndjson")

    def read(self, path: str | Path, **options: Any) -> RowList:
        path = Path(path)
        if not path.exists():
            raise ConnectorError(f"File not found: {path}")

        encoding = options.get("encoding", "utf-8")
        rows: RowList = []
        with path.open(encoding=encoding) as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ConnectorError(f"Invalid JSON on line {line_no}: {exc}") from exc
                if not isinstance(row, dict):
                    raise ConnectorError(f"Line {line_no} must be a JSON object")
                rows.append(row)
        return rows

    def write(self, path: str | Path, rows: RowList, **options: Any) -> None:
        path = Path(path)
        encoding = options.get("encoding", "utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding=encoding) as fh:
            for row in rows:
                fh.write(json.dumps(row, default=str) + "\n")
