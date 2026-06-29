"""Runtime index registry — primary, secondary, hash, inverted."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from index.btree import BPlusTree
from index.inverted import InvertedIndex


class IndexType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HASH = "hash"
    INVERTED = "inverted"


@dataclass
class IndexDefinition:
    name: str
    index_type: IndexType
    namespace: str
    fields: list[str]
    unique: bool = False


class IndexRegistry:
    def __init__(self):
        self.definitions: dict[str, IndexDefinition] = {}
        self._primary: dict[str, BPlusTree] = {}
        self._secondary: dict[str, BPlusTree] = {}
        self._hash: dict[str, dict] = {}
        self._inverted: dict[str, InvertedIndex] = {}

    def register(self, definition: IndexDefinition) -> None:
        self.definitions[definition.name] = definition
        if definition.index_type == IndexType.PRIMARY:
            self._primary[definition.namespace] = BPlusTree()
        elif definition.index_type == IndexType.SECONDARY:
            self._secondary[definition.name] = BPlusTree()
        elif definition.index_type == IndexType.HASH:
            self._hash[definition.name] = {}
        elif definition.index_type == IndexType.INVERTED:
            field_name = definition.fields[0]
            self._inverted[definition.name] = InvertedIndex(definition.name, field_name)

    def index_primary(self, namespace: str, key: str, storage_key: str) -> None:
        tree = self._primary.setdefault(namespace, BPlusTree())
        tree.insert(key, storage_key)

    def lookup_primary(self, namespace: str, key: str) -> str | None:
        tree = self._primary.get(namespace)
        return tree.lookup(key) if tree else None

    def index_secondary(self, index_name: str, key: str, record_id: str) -> None:
        tree = self._secondary.get(index_name)
        if tree:
            tree.insert(key, record_id)

    def lookup_secondary(self, index_name: str, key: str) -> str | None:
        tree = self._secondary.get(index_name)
        return tree.lookup(key) if tree else None

    def index_hash(self, index_name: str, key: str, record_id: str) -> None:
        bucket = self._hash.setdefault(index_name, {})
        bucket[key] = record_id

    def index_inverted(self, index_name: str, doc_id: str, data: dict) -> None:
        inverted = self._inverted.get(index_name)
        if inverted:
            inverted.index_document(doc_id, data)

    def search_inverted(self, index_name: str, term: str) -> set[str]:
        inverted = self._inverted.get(index_name)
        return inverted.search(term) if inverted else set()
