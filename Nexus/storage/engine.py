"""Unified key-value storage engine."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from storage.encoding import PayloadKind, decode_payload, encode_payload
from storage.namespace import NamespaceKind, storage_key


class StorageEngine:
    """Low-level put/get/scan over encoded payloads."""

    def __init__(self, data_dir: Path | None = None):
        self._data: dict[str, bytes] = {}
        self.data_dir = data_dir

    def put_row(self, table_name: str, row_id: str, values: dict) -> str:
        key = storage_key(NamespaceKind.TABLE, table_name, row_id)
        self._data[key] = encode_payload(PayloadKind.ROW, table_name, row_id, values)
        return key

    def put_document(self, collection_name: str, doc_id: str, data: dict) -> str:
        key = storage_key(NamespaceKind.COLLECTION, collection_name, doc_id)
        self._data[key] = encode_payload(PayloadKind.DOCUMENT, collection_name, doc_id, data)
        return key

    def get(self, kind: NamespaceKind, namespace: str, record_id: str) -> dict | None:
        key = storage_key(kind, namespace, record_id)
        raw = self._data.get(key)
        if raw is None:
            return None
        envelope = decode_payload(raw)
        return envelope["body"]

    def delete(self, kind: NamespaceKind, namespace: str, record_id: str) -> bool:
        key = storage_key(kind, namespace, record_id)
        return self._data.pop(key, None) is not None

    def scan(self, kind: NamespaceKind, namespace: str) -> Iterator[tuple[str, dict]]:
        prefix = f"{kind.value}:{namespace}:"
        for key, raw in sorted(self._data.items()):
            if not key.startswith(prefix):
                continue
            envelope = decode_payload(raw)
            yield envelope["key"], envelope["body"]

    def flush(self) -> None:
        if self.data_dir is None:
            return
        self.data_dir.mkdir(parents=True, exist_ok=True)
        snapshot = Path(self.data_dir) / "snapshot.kv"
        lines = [f"{k}\t{v.hex()}\n" for k, v in self._data.items()]
        snapshot.write_text("".join(lines), encoding="utf-8")
