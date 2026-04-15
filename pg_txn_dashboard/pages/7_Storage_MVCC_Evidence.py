import pandas as pd
import streamlit as st

from db import (
    get_table_indexes,
    get_table_storage_stats,
    run_bulk_asset_update,
    run_mvcc_tuple_demo,
    vacuum_analyze_table,
)
from utils import render_dataframe, render_internal_note


st.title("Storage and MVCC Evidence")
st.write(
    """
    This page turns the report's storage and MVCC claims into observable PostgreSQL evidence:
    tuple-version changes, dead tuples, relation size growth, and the cleanup role of VACUUM.
    """
)

st.subheader("Tuple Version Demo")
st.write(
    """
    The button below updates a `users` row inside a transaction, reads the system columns before
    and after the update, and then rolls the whole transaction back. That lets the app show how
    PostgreSQL creates a new tuple version without permanently changing your dataset.
    """
)

with st.form("mvcc_tuple_demo_form"):
    mvcc_user_id = st.number_input("User ID for tuple demo", min_value=1, value=1, step=1)
    mvcc_submitted = st.form_submit_button("Run MVCC Tuple Demo")

if mvcc_submitted:
    try:
        result = run_mvcc_tuple_demo(int(mvcc_user_id))
        if result["before"] is None:
            st.error("User not found.")
        else:
            st.success("Demo complete. The transaction was rolled back after capturing the evidence.")
            render_dataframe(pd.DataFrame([
                {"state": "before update", **result["before"]},
                {"state": "after update", **result["after"]},
            ]))
    except Exception as exc:
        st.error(f"MVCC demo failed: {exc}")

render_internal_note(
    "Why this matters",
    """
    A changed `ctid` means the row moved to a new physical tuple location in the heap. A changed
    `xmin` shows the row version was created by a new transaction. That is direct evidence that
    PostgreSQL updates rows by creating a new tuple version rather than overwriting in place.
    """,
)

st.subheader("Table Storage Stats")
selected_table = st.selectbox("Choose a table", ["users", "assets", "transactions", "logs"])

if st.button("Refresh Table Stats"):
    try:
        stats = get_table_storage_stats(selected_table)
        indexes = get_table_indexes(selected_table)
        if stats is None:
            st.error("Could not find stats for that table.")
        else:
            render_dataframe(pd.DataFrame([stats]))
            if indexes:
                st.markdown("**Indexes on this table**")
                render_dataframe(pd.DataFrame(indexes))
    except Exception as exc:
        st.error(f"Could not load storage stats: {exc}")

render_internal_note(
    "How to interpret these stats",
    """
    `n_dead_tup` is the most direct app-friendly signal of MVCC storage overhead. Heap size shows
    the table's own storage footprint, while index size shows the extra space and maintenance cost
    from secondary indexes.
    """,
)

st.subheader("Committed Bulk UPDATE on Assets")
st.warning(
    "This experiment makes a real committed change to the `assets` table so you can observe dead tuples and post-update storage effects."
)

with st.form("bulk_asset_update_form"):
    asset_start_id = st.number_input("Starting asset ID", min_value=1, value=1, step=1)
    asset_row_count = st.number_input("Number of asset rows to update", min_value=1, max_value=5000, value=100, step=1)
    asset_delta = st.number_input("Value increment to apply", value=1, step=1)
    bulk_update_submitted = st.form_submit_button("Run Committed Bulk UPDATE")

if bulk_update_submitted:
    try:
        outcome = run_bulk_asset_update(int(asset_start_id), int(asset_row_count), int(asset_delta))
        st.success(
            f"Updated {outcome['affected_rows']} asset rows from id {outcome['start_id']} through {outcome['end_id']}."
        )
        render_dataframe(
            pd.DataFrame(
                [
                    {"state": "before update", **outcome["before_stats"]},
                    {"state": "after update + ANALYZE", **outcome["after_stats"]},
                ]
            )
        )
    except Exception as exc:
        st.error(f"Bulk update failed: {exc}")

col1, col2 = st.columns(2)
with col1:
    if st.button("VACUUM ANALYZE assets"):
        try:
            vacuum_analyze_table("assets")
            st.success("VACUUM ANALYZE completed for assets.")
        except Exception as exc:
            st.error(f"VACUUM failed: {exc}")

with col2:
    if st.button("Refresh assets stats after VACUUM"):
        try:
            stats = get_table_storage_stats("assets")
            if stats is not None:
                render_dataframe(pd.DataFrame([stats]))
        except Exception as exc:
            st.error(f"Could not refresh assets stats: {exc}")

render_internal_note(
    "Report alignment",
    """
    This page covers the report's MVCC tuple-version experiment, dead tuple observation through
    `pg_stat_user_tables`, and the before/after storage story around bulk updates and VACUUM.
    If your local PostgreSQL instance has `pageinspect`, you can extend this further with raw page inspection.
    """,
)
