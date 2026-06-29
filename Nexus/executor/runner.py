"""Execute logical query plans against storage."""

from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING, Any, Callable

from planner.plan import LogicalQueryPlan, OpKind
from storage.namespace import NamespaceKind

if TYPE_CHECKING:
    from index.registry import IndexRegistry
    from storage.engine import StorageEngine
    from validator.manager import Validator


class PlanExecutor:
    def __init__(
        self,
        *,
        storage: "StorageEngine",
        indexes: "IndexRegistry",
        validator: "Validator",
        write_row: Callable[[str, str, dict], str],
        write_document: Callable[[str, str, dict], str],
        delete_record: Callable[[NamespaceKind, str, str], None],
        next_row_id: Callable[[str], int],
    ):
        self.storage = storage
        self.indexes = indexes
        self.validator = validator
        self._write_row = write_row
        self._write_document = write_document
        self._delete = delete_record
        self._next_row_id = next_row_id

    def execute(self, plan: LogicalQueryPlan) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for step in plan.steps:
            kind = NamespaceKind.TABLE if step.namespace_kind == "table" else NamespaceKind.COLLECTION

            if step.op == OpKind.SCAN:
                if "inverted_index" in step.params:
                    doc_ids = self.indexes.search_inverted(
                        step.params["inverted_index"],
                        step.params["term"],
                    )
                    rows = [
                        {"_id": doc_id, **(self.storage.get(kind, step.namespace, doc_id) or {})}
                        for doc_id in doc_ids
                    ]
                else:
                    rows = [
                        {"_id": rid, **body} if kind == NamespaceKind.COLLECTION else body
                        for rid, body in self.storage.scan(kind, step.namespace)
                    ]

            elif step.op == OpKind.FILTER:
                rows = [r for r in rows if self._matches_filter(r, step.params)]

            elif step.op == OpKind.PROJECT:
                cols = step.params.get("columns", ["*"])
                if cols == ["*"]:
                    continue
                rows = [{c: r.get(c) for c in cols} for r in rows]

            elif step.op == OpKind.INSERT:
                values = step.params["values"]
                if kind == NamespaceKind.TABLE:
                    values = self.validator.validate_row(step.namespace, values)
                    row_id = str(self._next_row_id(step.namespace))
                    values.setdefault("id", int(row_id))
                    self._write_row(step.namespace, row_id, values)
                    rows = [values]
                else:
                    values = self.validator.validate_document(step.namespace, values)
                    doc_id = str(uuid.uuid4())
                    self._write_document(step.namespace, doc_id, values)
                    rows = [{"_id": doc_id, **values}]

            elif step.op == OpKind.UPDATE:
                updated = []
                for rid, body in list(self.storage.scan(kind, step.namespace)):
                    record = {"_id": rid, **body} if kind == NamespaceKind.COLLECTION else body
                    if not self._matches_filter(record, step.params):
                        continue
                    assignments = step.params.get("assignments", {})
                    body.update(assignments)
                    if kind == NamespaceKind.TABLE:
                        body = self.validator.validate_row(step.namespace, body)
                        self._write_row(step.namespace, rid, body)
                    else:
                        body = self.validator.validate_document(step.namespace, body)
                        self._write_document(step.namespace, rid, body)
                    updated.append(record)
                rows = updated

            elif step.op == OpKind.DELETE:
                to_delete = []
                for rid, body in list(self.storage.scan(kind, step.namespace)):
                    record = {"_id": rid, **body} if kind == NamespaceKind.COLLECTION else body
                    if self._matches_filter(record, step.params):
                        to_delete.append(rid)
                for rid in to_delete:
                    self._delete(kind, step.namespace, rid)
                rows = [{"deleted": rid} for rid in to_delete]

        return rows

    @staticmethod
    def _matches_filter(record: dict, params: dict) -> bool:
        if "filter" in params:
            return all(record.get(k) == v for k, v in params["filter"].items())
        predicate = params.get("predicate")
        if not predicate:
            return True
        match = re.match(r"(\w+)\s*=\s*'?([^']+)'?", predicate.strip())
        if match:
            col, val = match.group(1), match.group(2)
            if val.upper() == "NULL":
                return record.get(col) is None
            return str(record.get(col)) == val
        return True
