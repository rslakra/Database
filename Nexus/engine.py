"""Multi-model database engine — SQL tables and document collections."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from catalog.metadata import Metadata
from catalog.table import Table
from document.collection import Collection
from document.document import Document
from executor.runner import PlanExecutor
from index.registry import IndexDefinition, IndexRegistry, IndexType
from parser.document import DocumentQuery, NoSQLQuery
from parser.sql import SQLParser
from planner.optimizer import Optimizer
from planner.plan import LogicalQueryPlan
from relational.row import Record, Row
from storage.engine import StorageEngine
from storage.namespace import NamespaceKind
from transaction.mvcc import MVCC
from transaction.wal import WalOp, WriteAheadLog
from validator.manager import SchemaManager, Validator

if TYPE_CHECKING:
    from dataio.service import DataPort


class MultiModelDatabase:
    """Hybrid SQL + document database with shared storage, indexes, WAL, and MVCC."""

    def __init__(self, name: str, *, data_dir: str | Path | None = None):
        self.metadata = Metadata(name=name)
        self.data_dir = Path(data_dir) if data_dir else None
        self.storage = StorageEngine(self.data_dir)
        self.indexes = IndexRegistry()
        self.validator = Validator()
        self.schema = self.validator  # backward-compatible alias
        self.wal = WriteAheadLog(self.data_dir / "wal.log" if self.data_dir else None)
        self.mvcc = MVCC()
        self.sql = SQLParser()
        self.documents = DocumentQuery()
        self.nosql = self.documents  # backward-compatible alias
        self.optimizer = Optimizer()
        self._row_id_counters: dict[str, int] = {}
        self._data_port: DataPort | None = None
        self._executor = PlanExecutor(
            storage=self.storage,
            indexes=self.indexes,
            validator=self.validator,
            write_row=self._write_row,
            write_document=self._write_document,
            delete_record=self._delete,
            next_row_id=self._next_row_id,
        )

    @property
    def data(self) -> "DataPort":
        if self._data_port is None:
            from dataio.service import DataPort

            self._data_port = DataPort(self)
        return self._data_port

    def create_table(self, table: Table) -> None:
        self.validator.register_table(table)
        self.metadata.tables.append(table)
        pk_cols: list[str] = []
        for constraint in table.constraints:
            if constraint.kind == "primary_key":
                pk_cols = constraint.columns
                break
        self.indexes.register(
            IndexDefinition(
                name=f"pk_{table.name}",
                index_type=IndexType.PRIMARY,
                namespace=table.name,
                fields=pk_cols or ["id"],
                unique=True,
            )
        )

    def create_collection(self, collection: Collection) -> None:
        self.validator.register_collection(collection)
        self.metadata.collections.append(collection)
        self.indexes.register(
            IndexDefinition(
                name=f"pk_{collection.name}",
                index_type=IndexType.PRIMARY,
                namespace=collection.name,
                fields=["_id"],
                unique=True,
            )
        )

    def create_index(
        self,
        name: str,
        *,
        namespace: str,
        fields: list[str],
        index_type: IndexType = IndexType.SECONDARY,
        unique: bool = False,
    ) -> None:
        self.indexes.register(
            IndexDefinition(
                name=name,
                index_type=index_type,
                namespace=namespace,
                fields=fields,
                unique=unique,
            )
        )

    def create_text_index(self, name: str, *, collection: str, field: str) -> None:
        self.indexes.register(
            IndexDefinition(
                name=name,
                index_type=IndexType.INVERTED,
                namespace=collection,
                fields=[field],
            )
        )

    def execute_sql(self, sql: str) -> list[dict[str, Any]]:
        plan = self.optimizer.optimize(self.sql.parse(sql))
        return self._executor.execute(plan)

    def execute_nosql(self, plan: LogicalQueryPlan) -> list[dict[str, Any]]:
        plan = self.optimizer.optimize(plan)
        return self._executor.execute(plan)

    def insert_row(self, row: Row) -> str:
        table_name = row.table.name
        values = self.validator.validate_row(table_name, row.values)
        row_id = str(self._next_row_id(table_name))
        values.setdefault("id", int(row_id))
        return self._write_row(table_name, row_id, values)

    def insert_record(self, record: Record) -> str:
        return self.insert_row(record)

    def insert_document(self, document: Document) -> str:
        collection_name = document.collection.name
        data = self.validator.validate_document(collection_name, document.data)
        return self._write_document(collection_name, document.doc_id, data)

    def fetch_table_rows(self, table_name: str) -> list[dict[str, Any]]:
        return [body for _, body in self.storage.scan(NamespaceKind.TABLE, table_name)]

    def fetch_collection_docs(self, collection_name: str) -> list[dict[str, Any]]:
        return [
            {"_id": doc_id, **body}
            for doc_id, body in self.storage.scan(NamespaceKind.COLLECTION, collection_name)
        ]

    def _write_row(self, table_name: str, row_id: str, values: dict) -> str:
        self.wal.append(
            WalOp.INSERT,
            namespace_kind="table",
            namespace=table_name,
            record_id=row_id,
            payload=values,
        )
        self.mvcc.write("table", table_name, row_id, values)
        storage_key = self.storage.put_row(table_name, row_id, values)
        self.indexes.index_primary(table_name, row_id, storage_key)
        for index_name, definition in self.indexes.definitions.items():
            if definition.namespace != table_name:
                continue
            if definition.index_type == IndexType.SECONDARY:
                for field in definition.fields:
                    if field in values:
                        self.indexes.index_secondary(index_name, str(values[field]), row_id)
        return row_id

    def _write_document(self, collection_name: str, doc_id: str, data: dict) -> str:
        self.wal.append(
            WalOp.INSERT,
            namespace_kind="collection",
            namespace=collection_name,
            record_id=doc_id,
            payload=data,
        )
        self.mvcc.write("collection", collection_name, doc_id, data)
        storage_key = self.storage.put_document(collection_name, doc_id, data)
        self.indexes.index_primary(collection_name, doc_id, storage_key)
        for index_name, definition in self.indexes.definitions.items():
            if definition.namespace != collection_name:
                continue
            if definition.index_type == IndexType.INVERTED:
                self.indexes.index_inverted(index_name, doc_id, data)
            elif definition.index_type == IndexType.SECONDARY:
                for field in definition.fields:
                    if field in data:
                        self.indexes.index_secondary(index_name, str(data[field]), doc_id)
        return doc_id

    def _delete(self, kind: NamespaceKind, namespace: str, record_id: str) -> None:
        self.wal.append(
            WalOp.DELETE,
            namespace_kind=kind.value,
            namespace=namespace,
            record_id=record_id,
            payload={},
        )
        self.storage.delete(kind, namespace, record_id)

    def _next_row_id(self, table_name: str) -> int:
        self._row_id_counters[table_name] = self._row_id_counters.get(table_name, 0) + 1
        return self._row_id_counters[table_name]

    def recover(self) -> int:
        entries = self.wal.replay()
        for entry in entries:
            kind = NamespaceKind(entry.namespace_kind)
            if entry.op == WalOp.INSERT:
                if kind == NamespaceKind.TABLE:
                    self.storage.put_row(entry.namespace, entry.record_id, entry.payload)
                else:
                    self.storage.put_document(entry.namespace, entry.record_id, entry.payload)
            elif entry.op == WalOp.DELETE:
                self.storage.delete(kind, entry.namespace, entry.record_id)
        return len(entries)

    def flush(self) -> None:
        self.storage.flush()
