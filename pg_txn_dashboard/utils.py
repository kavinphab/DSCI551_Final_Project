from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from db import explain_analyze, get_user_workspace_summary
from plan_utils import format_plan_summary, summarize_plan
from queries import OPERATION_DETAILS


def render_sql(sql: str) -> None:
    st.code(sql.strip(), language="sql")


def render_dataframe(df: pd.DataFrame) -> None:
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_internal_note(title: str, body: str) -> None:
    st.markdown(f"**{title}**")
    st.write(body)


def _plan_uses_index(summary: dict) -> bool:
    return any("Index" in operator for operator in summary["operators_seen"])


def ensure_workspace_state() -> None:
    st.session_state.setdefault("active_user_id", 1)
    st.session_state.setdefault("active_asset_id", 1)
    st.session_state.setdefault("default_row_limit", 25)
    st.session_state.setdefault("sidebar_active_user_id", st.session_state["active_user_id"])
    st.session_state.setdefault("sidebar_active_asset_id", st.session_state["active_asset_id"])
    st.session_state.setdefault("sidebar_default_row_limit", st.session_state["default_row_limit"])


def update_workspace_context(user_id: int | None = None, asset_id: int | None = None, row_limit: int | None = None) -> None:
    if user_id is not None:
        st.session_state["active_user_id"] = int(user_id)
    if asset_id is not None:
        st.session_state["active_asset_id"] = int(asset_id)
    if row_limit is not None:
        st.session_state["default_row_limit"] = int(row_limit)


def sync_workspace_from_sidebar() -> None:
    st.session_state["active_user_id"] = int(st.session_state["sidebar_active_user_id"])
    st.session_state["active_asset_id"] = int(st.session_state["sidebar_active_asset_id"])
    st.session_state["default_row_limit"] = int(st.session_state["sidebar_default_row_limit"])


def render_workspace_sidebar() -> dict:
    ensure_workspace_state()

    with st.sidebar:
        st.header("Platform Controls")
        st.caption("Carry one investigation context across the whole dashboard.")
        st.number_input(
            "Active user ID",
            min_value=1,
            step=1,
            key="sidebar_active_user_id",
            on_change=sync_workspace_from_sidebar,
        )
        st.number_input(
            "Active asset ID",
            min_value=1,
            step=1,
            key="sidebar_active_asset_id",
            on_change=sync_workspace_from_sidebar,
        )
        st.number_input(
            "Default row limit",
            min_value=1,
            max_value=1000,
            step=1,
            key="sidebar_default_row_limit",
            on_change=sync_workspace_from_sidebar,
        )

        st.markdown("**Main workflows**")
        st.page_link("app.py", label="Overview")
        st.page_link("pages/2_Search_Explore_Transactions.py", label="Search & explore")
        st.page_link("pages/3_Recent_Activity_Feed.py", label="Recent activity")
        st.page_link("pages/4_Analytics_Summaries.py", label="Analytics & summaries")
        st.page_link("pages/5_Update_Record_Activity.py", label="Update & record activity")

        st.markdown("**Advanced evidence**")
        st.page_link("pages/6_Advanced_Database_Insights.py", label="Advanced query plans")
        st.page_link("pages/7_Storage_MVCC_Evidence.py", label="Storage & MVCC evidence")
        st.page_link("pages/8_Concurrency_and_Insert_Benchmark.py", label="Concurrency & write behavior")
        st.page_link("pages/9_Admin_Setup.py", label="Admin & setup")

        st.markdown("**Suggested workflow**")
        st.markdown(
            """
            1. Search and explore a user's transactions.
            2. Review recent activity and summary metrics.
            3. Expand Database Insights on the same page.
            4. Use the advanced evidence pages only when you want a deeper PostgreSQL explanation.
            """
        )

        try:
            summary = get_user_workspace_summary(int(st.session_state["active_user_id"]))
            if summary:
                st.markdown("**Active user snapshot**")
                st.write(f"{summary['name']} ({summary['email']})")
                col1, col2 = st.columns(2)
                col1.metric("Transactions", f"{summary['txn_count']}")
                col2.metric("Assets", f"{summary['asset_count']}")
                if summary["last_transaction_at"]:
                    st.caption(f"Latest transaction: {summary['last_transaction_at']}")
            else:
                st.caption("No user found for the active context.")
        except Exception:
            st.caption("Connect the database to enable the active user snapshot.")

    return {
        "active_user_id": int(st.session_state["active_user_id"]),
        "active_asset_id": int(st.session_state["active_asset_id"]),
        "default_row_limit": int(st.session_state["default_row_limit"]),
    }


def render_page_intro(title: str, description: str, next_steps: list[tuple[str, str]] | None = None) -> None:
    context = {
        "user_id": st.session_state.get("active_user_id", 1),
        "asset_id": st.session_state.get("active_asset_id", 1),
        "row_limit": st.session_state.get("default_row_limit", 25),
    }
    st.title(title)
    st.write(description)

    col1, col2, col3 = st.columns(3)
    col1.metric("Active user", context["user_id"])
    col2.metric("Active asset", context["asset_id"])
    col3.metric("Default row limit", context["row_limit"])

    if next_steps:
        st.markdown("**Recommended next steps**")
        cols = st.columns(len(next_steps))
        for col, (page_path, label) in zip(cols, next_steps):
            col.page_link(page_path, label=label)


def render_workflow_panel(title: str, description: str, page_path: str, button_label: str) -> None:
    st.markdown(f"### {title}")
    st.write(description)
    st.page_link(page_path, label=button_label)


def render_database_insights_panel(operation_name: str, params: tuple, query_label: str | None = None) -> None:
    details = OPERATION_DETAILS[operation_name]
    label = query_label or operation_name

    with st.expander(f"Database Insights: {label}", expanded=False):
        try:
            render_custom_database_insights_panel(
                sql=details["sql"],
                params=params,
                explanation=details["plan_explanation"],
                label=label,
            )
        except Exception as exc:
            st.error(f"Could not load database insights: {exc}")


def render_custom_database_insights_panel(sql: str, params: tuple, explanation: str, label: str) -> None:
    plan_result = explain_analyze(sql, params)
    summary = summarize_plan(plan_result)

    st.markdown("**SQL query used by this workflow**")
    render_sql(sql)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Main operator", summary["main_operator"])
    col2.metric("Index used", "Yes" if _plan_uses_index(summary) else "No")
    col3.metric("Planning ms", f"{summary['planning_time_ms']:.3f}")
    col4.metric("Execution ms", f"{summary['execution_time_ms']:.3f}")

    st.markdown("**Simplified plan summary**")
    st.code(format_plan_summary(summary), language="text")

    st.markdown("**Why PostgreSQL chose this plan**")
    st.write(explanation)

    with st.expander("Raw EXPLAIN ANALYZE output"):
        st.code(json.dumps(plan_result, indent=2), language="json")


def render_explain_section(operation_name: str, params: tuple) -> None:
    details = OPERATION_DETAILS[operation_name]
    sql = details["sql"]
    plan_result = explain_analyze(sql, params)
    summary = summarize_plan(plan_result)

    st.markdown("**SQL used by the app**")
    render_sql(sql)

    col1, col2, col3 = st.columns(3)
    col1.metric("Main operator", summary["main_operator"])
    col2.metric("Planning time (ms)", f"{summary['planning_time_ms']:.3f}")
    col3.metric("Execution time (ms)", f"{summary['execution_time_ms']:.3f}")

    st.markdown("**Simplified plan summary**")
    st.code(format_plan_summary(summary), language="text")

    st.markdown("**Why this internal behavior matters**")
    st.write(details["plan_explanation"])

    with st.expander("Raw EXPLAIN ANALYZE output"):
        st.code(json.dumps(plan_result, indent=2), language="json")
