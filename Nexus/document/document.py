"""One document in a collection."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from document.collection import Collection


class Document:
    def __init__(
        self,
        *,
        collection: "Collection",
        data: dict[str, Any],
        doc_id: str | None = None,
        version: int = 0,
    ):
        self.collection = collection
        self.doc_id = doc_id or str(uuid.uuid4())
        self.data = data
        self.version = version

    def get(self, path: str, default=None):
        node: Any = self.data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node
