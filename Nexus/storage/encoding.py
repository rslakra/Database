"""Unified binary encoding for SQL rows and NoSQL documents.

Converts structured Python values into a single on-disk representation
(JSON + length prefix). Production systems often use BSON or Protocol Buffers;
this module uses a portable JSON envelope for the learning implementation.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any


class PayloadKind(str, Enum):
    ROW = "row"
    DOCUMENT = "document"


def encode_payload(kind: PayloadKind, namespace: str, key: str, body: dict[str, Any]) -> bytes:
    """Serialize a row or document into bytes for the storage engine."""
    envelope = {
        "kind": kind.value,
        "namespace": namespace,
        "key": key,
        "body": body,
    }
    return json.dumps(envelope, separators=(",", ":"), default=str).encode("utf-8")


def decode_payload(data: bytes) -> dict[str, Any]:
    """Deserialize bytes back into an envelope dict."""
    return json.loads(data.decode("utf-8"))
