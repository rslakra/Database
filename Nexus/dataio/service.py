"""Import and export bridge between files and MultiModelDatabase."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from dataio.base import DataConnector
from dataio.registry import get_connector, get_connector_for_path
from document.document import Document
from relational.row import Row
from datatype.data_formats import DataFormat, RowList

if TYPE_CHECKING:
    from engine import MultiModelDatabase


class DataPort:
    """Ingest external files into tables/collections and export data back out."""

    def __init__(self, db: "MultiModelDatabase"):
        self.db = db

    # -- Import ----------------------------------------------------------------

    def import_table(
        self,
        path: str | Path,
        table_name: str,
        *,
        fmt: str | DataFormat | None = None,
        connector: DataConnector | None = None,
        **options: Any,
    ) -> int:
        """Load rows from a file into a registered SQL table. Returns row count."""
        conn = connector or (get_connector(fmt) if fmt else get_connector_for_path(path))
        rows = conn.read(path, **options)
        table = self.db.validator.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table not registered: {table_name}")

        count = 0
        for row in rows:
            clean = {k: v for k, v in row.items() if k != "id"}
            self.db.insert_record(Row(table=table, values=clean))
            count += 1
        return count

    def import_collection(
        self,
        path: str | Path,
        collection_name: str,
        *,
        fmt: str | DataFormat | None = None,
        connector: DataConnector | None = None,
        **options: Any,
    ) -> int:
        """Load documents from a file into a registered NoSQL collection."""
        conn = connector or (get_connector(fmt) if fmt else get_connector_for_path(path))
        rows = conn.read(path, **options)
        collection = self.db.validator.collections.get(collection_name)
        if collection is None:
            raise ValueError(f"Collection not registered: {collection_name}")

        count = 0
        for row in rows:
            doc_id = row.pop("_id", None)
            self.db.insert_document(
                Document(collection=collection, data=dict(row), doc_id=doc_id)
            )
            count += 1
        return count

    # -- Export ----------------------------------------------------------------

    def export_table(
        self,
        path: str | Path,
        table_name: str,
        *,
        fmt: str | DataFormat | None = None,
        connector: DataConnector | None = None,
        **options: Any,
    ) -> int:
        """Write all rows from a SQL table to a file."""
        conn = connector or (get_connector(fmt) if fmt else get_connector_for_path(path))
        rows = self.db.fetch_table_rows(table_name)
        conn.write(path, rows, **options)
        return len(rows)

    def export_collection(
        self,
        path: str | Path,
        collection_name: str,
        *,
        fmt: str | DataFormat | None = None,
        connector: DataConnector | None = None,
        **options: Any,
    ) -> int:
        """Write all documents from a NoSQL collection to a file."""
        conn = connector or (get_connector(fmt) if fmt else get_connector_for_path(path))
        rows = self.db.fetch_collection_docs(collection_name)
        conn.write(path, rows, **options)
        return len(rows)

    # -- Generic read/write (no database) --------------------------------------

    @staticmethod
    def read_file(
        path: str | Path,
        *,
        fmt: str | DataFormat | None = None,
        **options: Any,
    ) -> RowList:
        conn = get_connector(fmt) if fmt else get_connector_for_path(path)
        return conn.read(path, **options)

    @staticmethod
    def write_file(
        path: str | Path,
        rows: RowList,
        *,
        fmt: str | DataFormat | None = None,
        **options: Any,
    ) -> None:
        conn = get_connector(fmt) if fmt else get_connector_for_path(path)
        conn.write(path, rows, **options)
