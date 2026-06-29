"""Database catalog — name, namespaces, access rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from catalog.access import Access
    from catalog.table import Table
    from document.collection import Collection


@dataclass
class Metadata:
    name: str
    charset: str = "utf8mb4"
    tables: list["Table"] = field(default_factory=list)
    collections: list["Collection"] = field(default_factory=list)
    access_rules: list["Access"] = field(default_factory=list)
    engine_version: str = "0.3.0"
