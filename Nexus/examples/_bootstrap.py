"""Ensure Nexus project root is on sys.path when running examples."""

import sys
from pathlib import Path


def bootstrap() -> Path:
    root = Path(__file__).resolve().parent.parent
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root
