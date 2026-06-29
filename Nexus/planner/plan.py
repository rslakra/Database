"""Logical query plan operators."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OpKind(str, Enum):
    SCAN = "scan"
    FILTER = "filter"
    PROJECT = "project"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class PlanStep:
    op: OpKind
    namespace: str
    namespace_kind: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class LogicalQueryPlan:
    steps: list[PlanStep] = field(default_factory=list)
    source: str = "sql"

    def add(self, step: PlanStep) -> "LogicalQueryPlan":
        self.steps.append(step)
        return self
