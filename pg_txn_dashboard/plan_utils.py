from __future__ import annotations

from typing import Any


def _walk_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = [plan]
    for child in plan.get("Plans", []):
        nodes.extend(_walk_plan(child))
    return nodes


def summarize_plan(explain_result: list[dict[str, Any]]) -> dict[str, Any]:
    root = explain_result[0]
    plan = root["Plan"]
    nodes = _walk_plan(plan)

    operators = []
    for node in nodes:
        name = node.get("Node Type", "Unknown")
        if name not in operators:
            operators.append(name)

    return {
        "main_operator": plan.get("Node Type", "Unknown"),
        "operators_seen": operators,
        "planning_time_ms": root.get("Planning Time"),
        "execution_time_ms": root.get("Execution Time"),
        "plan_rows": plan.get("Plan Rows"),
        "actual_rows": plan.get("Actual Rows"),
        "total_cost": plan.get("Total Cost"),
    }


def format_plan_summary(summary: dict[str, Any]) -> str:
    operators = ", ".join(summary["operators_seen"])
    return (
        f"Main operator: {summary['main_operator']}\n"
        f"Operators seen: {operators}\n"
        f"Planning time: {summary['planning_time_ms']:.3f} ms\n"
        f"Execution time: {summary['execution_time_ms']:.3f} ms\n"
        f"Estimated rows at root: {summary['plan_rows']}\n"
        f"Actual rows at root: {summary['actual_rows']}\n"
        f"Estimated total cost: {summary['total_cost']}"
    )
