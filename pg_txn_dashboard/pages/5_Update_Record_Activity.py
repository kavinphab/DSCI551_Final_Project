import pandas as pd
import streamlit as st

from db import execute_write, fetch_one
from queries import GET_ASSET_SQL, INSERT_LOG_SQL, UPDATE_ASSET_SQL
from utils import (
    render_dataframe,
    render_internal_note,
    render_page_intro,
    render_sql,
    render_workspace_sidebar,
    update_workspace_context,
)


context = render_workspace_sidebar()
render_page_intro(
    "Update & Record Activity",
    "Use this page the way an internal operations team would: record an event, update an asset, confirm the change, and then open the embedded insights to connect the behavior to MVCC and write overhead.",
    next_steps=[
        ("pages/7_Storage_MVCC_Evidence.py", "Inspect MVCC evidence"),
        ("pages/8_Concurrency_and_Insert_Benchmark.py", "Inspect write behavior"),
    ],
)

tab1, tab2 = st.tabs(["Record a log event", "Update an asset"])

with tab1:
    with st.form("record_log_event_form"):
        event = st.text_input("Log event", value="Dashboard activity recorded from Streamlit")
        insert_submitted = st.form_submit_button("Insert Log Entry")

    if insert_submitted:
        if not event.strip():
            st.error("Please enter a non-empty log event.")
        else:
            try:
                rows, rowcount = execute_write(INSERT_LOG_SQL, (event.strip(),))
                st.success(f"Inserted {rowcount} log entry.")
                render_dataframe(pd.DataFrame(rows))
            except Exception as exc:
                st.error(f"Insert failed: {exc}")

    with st.expander("Database Insights: log insert", expanded=False):
        render_sql(INSERT_LOG_SQL)
        st.write(
            """
            Even a small insert is not just a table write. PostgreSQL records the change in WAL for durability and
            updates the relevant table and index structures behind the scenes.
            """
        )

with tab2:
    with st.form("update_asset_value_form"):
        asset_id = st.number_input("Asset ID", min_value=1, value=context["active_asset_id"], step=1)
        new_value = st.number_input("New asset value", value=100, step=1)
        update_submitted = st.form_submit_button("Update Asset Value")

    if update_submitted:
        update_workspace_context(asset_id=int(asset_id))
        try:
            before_row = fetch_one(GET_ASSET_SQL, (int(asset_id),))
            if before_row is None:
                st.error("Asset not found.")
            else:
                updated_rows, rowcount = execute_write(UPDATE_ASSET_SQL, (int(new_value), int(asset_id)))
                after_row = updated_rows[0] if updated_rows else None
                st.success(f"Updated {rowcount} asset row.")
                render_dataframe(pd.DataFrame([{"state": "before", **before_row}, {"state": "after", **after_row}]))
        except Exception as exc:
            st.error(f"Update failed: {exc}")

    with st.expander("Database Insights: asset update", expanded=False):
        render_sql(UPDATE_ASSET_SQL)
        st.write(
            """
            PostgreSQL updates are MVCC writes: the old tuple version is not overwritten in place. A new tuple version
            is created, the old one becomes dead to future transactions, and VACUUM later reclaims the space.
            """
        )

render_internal_note(
    "Operational meaning",
    """
    This page is deliberately framed as a system-of-record workflow. The user performs an action first and then
    optionally opens the database explanation, which makes the app feel more like a real internal platform.
    """,
)
