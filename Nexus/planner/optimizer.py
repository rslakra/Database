"""Query plan optimizer."""

from __future__ import annotations

from planner.plan import LogicalQueryPlan, OpKind


class Optimizer:
    def optimize(self, plan: LogicalQueryPlan) -> LogicalQueryPlan:
        optimized = LogicalQueryPlan(source=plan.source)
        pending_filter = None
        for step in plan.steps:
            if step.op == OpKind.SCAN:
                if pending_filter:
                    optimized.add(pending_filter)
                    pending_filter = None
                optimized.add(step)
            elif step.op == OpKind.FILTER and pending_filter is None:
                pending_filter = step
            else:
                if pending_filter:
                    optimized.add(pending_filter)
                    pending_filter = None
                optimized.add(step)
        if pending_filter:
            optimized.add(pending_filter)
        return optimized
