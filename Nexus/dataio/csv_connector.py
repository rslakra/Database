"""CSV file connector — stdlib only."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from dataio.base import ConnectorError, DataConnector
from datatype.data_formats import RowList


class CSVConnector(DataConnector):
    format_name = "csv"
    file_extensions = ("csv", "tsv")

    def read(self, path: str | Path, **options: Any) -> RowList:
        path = Path(path)
        if not path.exists():
            raise ConnectorError(f"File not found: {path}")

        delimiter = options.get("delimiter")
        if delimiter is None:
            delimiter = "\t" if path.suffix.lower() == ".tsv" else ","

        encoding = options.get("encoding", "utf-8")
        with path.open(newline="", encoding=encoding) as fh:
            reader = csv.DictReader(fh, delimiter=delimiter)
            return [_normalize_row(row) for row in reader]

    def write(self, path: str | Path, rows: RowList, **options: Any) -> None:
        path = Path(path)
        if not rows:
            raise ConnectorError("Cannot write CSV with zero rows")

        delimiter = options.get("delimiter", ",")
        encoding = options.get("encoding", "utf-8")
        fieldnames = options.get("fieldnames") or list(rows[0].keys())

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding=encoding) as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})


def _normalize_row(row: dict) -> dict:
    return {k: (v if v != "" else None) for k, v in row.items()}
