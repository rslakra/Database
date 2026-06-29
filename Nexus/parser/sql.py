"""SQL parser → logical plan."""

from __future__ import annotations

import re
from typing import Any

from planner.plan import LogicalQueryPlan, OpKind, PlanStep


class SQLParser:
    def parse(self, sql: str) -> LogicalQueryPlan:
        statement = sql.strip().rstrip(";")
        upper = statement.upper()

        if upper.startswith("SELECT"):
            return self._parse_select(statement)
        if upper.startswith("INSERT"):
            return self._parse_insert(statement)
        if upper.startswith("UPDATE"):
            return self._parse_update(statement)
        if upper.startswith("DELETE"):
            return self._parse_delete(statement)
        raise ValueError(f"Unsupported SQL: {statement[:40]}...")

    def _parse_select(self, sql: str) -> LogicalQueryPlan:
        match = re.match(
            r"SELECT\s+(?P<cols>.+?)\s+FROM\s+(?P<table>\w+)(?:\s+WHERE\s+(?P<where>.+))?$",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Invalid SELECT syntax")
        cols = [c.strip() for c in match.group("cols").split(",")]
        table = match.group("table")
        plan = LogicalQueryPlan(source="sql")
        plan.add(PlanStep(OpKind.SCAN, table, "table"))
        if match.group("where"):
            plan.add(PlanStep(OpKind.FILTER, table, "table", {"predicate": match.group("where")}))
        plan.add(PlanStep(OpKind.PROJECT, table, "table", {"columns": cols}))
        return plan

    def _parse_insert(self, sql: str) -> LogicalQueryPlan:
        match = re.match(
            r"INSERT\s+INTO\s+(?P<table>\w+)\s*\((?P<cols>[^)]+)\)\s*VALUES\s*\((?P<vals>[^)]+)\)",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Invalid INSERT syntax")
        columns = [c.strip() for c in match.group("cols").split(",")]
        raw_vals = [v.strip().strip("'").strip('"') for v in match.group("vals").split(",")]
        values = dict(zip(columns, _coerce_literals(raw_vals)))
        plan = LogicalQueryPlan(source="sql")
        plan.add(PlanStep(OpKind.INSERT, match.group("table"), "table", {"values": values}))
        return plan

    def _parse_update(self, sql: str) -> LogicalQueryPlan:
        match = re.match(
            r"UPDATE\s+(?P<table>\w+)\s+SET\s+(?P<set>.+?)(?:\s+WHERE\s+(?P<where>.+))?$",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        assignments = _parse_assignments(match.group("set"))
        plan = LogicalQueryPlan(source="sql")
        plan.add(
            PlanStep(
                OpKind.UPDATE,
                match.group("table"),
                "table",
                {"assignments": assignments, "predicate": match.group("where")},
            )
        )
        return plan

    def _parse_delete(self, sql: str) -> LogicalQueryPlan:
        match = re.match(
            r"DELETE\s+FROM\s+(?P<table>\w+)(?:\s+WHERE\s+(?P<where>.+))?$",
            sql,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Invalid DELETE syntax")
        plan = LogicalQueryPlan(source="sql")
        plan.add(
            PlanStep(OpKind.DELETE, match.group("table"), "table", {"predicate": match.group("where")})
        )
        return plan


def _parse_assignments(clause: str) -> dict[str, Any]:
    result = {}
    for part in clause.split(","):
        key, _, val = part.partition("=")
        result[key.strip()] = _coerce_literals([val.strip().strip("'").strip('"')])[0]
    return result


def _coerce_literals(values: list[str]) -> list[Any]:
    out = []
    for v in values:
        if v.upper() == "NULL":
            out.append(None)
        elif v.isdigit():
            out.append(int(v))
        else:
            out.append(v)
    return out
