"""Inverted index for full-text search on document fields."""

from __future__ import annotations

import re
from collections import defaultdict


class InvertedIndex:
    def __init__(self, name: str, field: str):
        self.name = name
        self.field = field
        self._postings: dict[str, set[str]] = defaultdict(set)

    def index_document(self, doc_id: str, data: dict) -> None:
        text = data.get(self.field)
        if text is None:
            return
        for token in _tokenize(str(text)):
            self._postings[token].add(doc_id)

    def remove_document(self, doc_id: str) -> None:
        for postings in self._postings.values():
            postings.discard(doc_id)

    def search(self, term: str) -> set[str]:
        return set(self._postings.get(term.lower(), ()))


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", text)]
