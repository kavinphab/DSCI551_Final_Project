from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from db import explain_analyze
from plan_utils import format_plan_summary, summarize_plan
from queries import OPERATION_DETAILS


def render_sql(sql: str) -> None:
    st.code(sql.strip(), language="sql")


def render_dataframe(df: pd.DataFrame) -> None:
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_internal_note(title: str, body: str) -> None:
    st.markdown(f"**{title}**")
    st.write(body)


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
