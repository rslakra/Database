"""Document query builder → logical plan."""

from __future__ import annotations

from typing import Any

from planner.plan import LogicalQueryPlan, OpKind, PlanStep


class DocumentQuery:
    def find(
        self,
        collection: str,
        *,
        filter: dict[str, Any] | None = None,
        projection: list[str] | None = None,
    ) -> LogicalQueryPlan:
        plan = LogicalQueryPlan(source="document")
        plan.add(PlanStep(OpKind.SCAN, collection, "collection"))
        if filter:
            plan.add(PlanStep(OpKind.FILTER, collection, "collection", {"filter": filter}))
        if projection:
            plan.add(PlanStep(OpKind.PROJECT, collection, "collection", {"columns": projection}))
        return plan

    def insert_one(self, collection: str, document: dict[str, Any]) -> LogicalQueryPlan:
        plan = LogicalQueryPlan(source="document")
        plan.add(PlanStep(OpKind.INSERT, collection, "collection", {"values": document}))
        return plan

    def update_many(
        self,
        collection: str,
        *,
        filter: dict[str, Any],
        set_fields: dict[str, Any],
    ) -> LogicalQueryPlan:
        plan = LogicalQueryPlan(source="document")
        plan.add(
            PlanStep(
                OpKind.UPDATE,
                collection,
                "collection",
                {"predicate_filter": filter, "assignments": set_fields},
            )
        )
        return plan

    def delete_many(self, collection: str, *, filter: dict[str, Any]) -> LogicalQueryPlan:
        plan = LogicalQueryPlan(source="document")
        plan.add(PlanStep(OpKind.DELETE, collection, "collection", {"predicate_filter": filter}))
        return plan

    def text_search(self, collection: str, *, index: str, term: str) -> LogicalQueryPlan:
        plan = LogicalQueryPlan(source="document")
        plan.add(
            PlanStep(
                OpKind.SCAN,
                collection,
                "collection",
                {"inverted_index": index, "term": term},
            )
        )
        return plan


# Backward-compatible alias
NoSQLQuery = DocumentQuery
