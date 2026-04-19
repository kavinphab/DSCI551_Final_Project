import json

import pandas as pd
import streamlit as st

from db import benchmark_insert_batches, explain_analyze_rolled_back, run_concurrent_mvcc_demo
from plan_utils import format_plan_summary, summarize_plan
from queries import LOG_INSERT_SQL, TRANSACTION_INSERT_SQL
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
    "Concurrency and Insert Benchmark",
    "Finish the investigation by validating snapshot isolation and measuring how much more work PostgreSQL performs for heavier transaction writes.",
    next_steps=[
        ("pages/6_Advanced_Database_Insights.py", "Return to query plans"),
        ("pages/9_Admin_Setup.py", "Review setup and indexes"),
    ],
)

st.subheader("Concurrent Read + Write MVCC Demo")
st.write(
    """
    The app opens two database sessions. Session A starts a `REPEATABLE READ` transaction and
    counts one user's transactions. Session B inserts a new transaction and commits. Session A
    reads again without seeing the new row, then a fresh read after commit sees it. The inserted
    row is deleted at the end so the demo stays tidy.
    """
)

with st.form("concurrency_demo_form"):
    concurrent_user_id = st.number_input("User ID for concurrency demo", min_value=1, value=context["active_user_id"], step=1)
    concurrent_asset_id = st.number_input("Asset ID for inserted transaction", min_value=1, value=context["active_asset_id"], step=1)
    concurrency_submitted = st.form_submit_button("Run Concurrent Read/Write Demo")

if concurrency_submitted:
    try:
        update_workspace_context(user_id=int(concurrent_user_id), asset_id=int(concurrent_asset_id))
        result = run_concurrent_mvcc_demo(int(concurrent_user_id), int(concurrent_asset_id))
        render_dataframe(
            pd.DataFrame(
                [
                    {"step": "count before writer commits", "txn_count": result["count_before"]},
                    {
                        "step": "count inside repeatable-read snapshot after writer commits",
                        "txn_count": result["count_during_repeatable_read"],
                    },
                    {"step": "count in fresh session after commit", "txn_count": result["count_after_commit"]},
                ]
            )
        )
        st.success(
            f"Inserted and cleaned up transaction id {result['inserted_transaction_id']} for user {result['user_id']}."
        )
    except Exception as exc:
        st.error(f"Concurrency demo failed: {exc}")

render_internal_note(
    "Why this matters",
    """
    This demonstrates MVCC snapshot isolation directly: readers are not blocked by writers, and a
    repeatable-read transaction continues to see the same snapshot even after another session commits.
    """,
)

st.subheader("High-Frequency Insert Benchmark")
st.write(
    """
    The benchmark below inserts a batch into `transactions` and a matching batch into `logs`,
    each inside a transaction that is rolled back afterward. That keeps the dataset stable while
    still measuring real insert work, including index maintenance on `transactions`.
    """
)

with st.form("insert_benchmark_form"):
    batch_size = st.number_input("Benchmark batch size", min_value=10, max_value=5000, value=500, step=10)
    sample_user_id = st.number_input("Sample user ID", min_value=1, value=context["active_user_id"], step=1)
    sample_asset_id = st.number_input("Sample asset ID", min_value=1, value=context["active_asset_id"], step=1)
    benchmark_submitted = st.form_submit_button("Run Insert Benchmark")

if benchmark_submitted:
    try:
        update_workspace_context(user_id=int(sample_user_id), asset_id=int(sample_asset_id))
        benchmark = benchmark_insert_batches(int(batch_size), int(sample_user_id), int(sample_asset_id))
        summary_df = pd.DataFrame(
            [
                {
                    "table": "transactions",
                    "batch_size": benchmark["batch_size"],
                    "elapsed_ms": round(benchmark["transactions_elapsed_ms"], 3),
                },
                {
                    "table": "logs",
                    "batch_size": benchmark["batch_size"],
                    "elapsed_ms": round(benchmark["logs_elapsed_ms"], 3),
                },
            ]
        )
        render_dataframe(summary_df)

        st.markdown("**Index footprint during the benchmark**")
        render_dataframe(
            pd.DataFrame(
                [
                    {"table": "transactions", "index_count": len(benchmark["transactions_indexes"])},
                    {"table": "logs", "index_count": len(benchmark["logs_indexes"])},
                ]
            )
        )
    except Exception as exc:
        st.error(f"Insert benchmark failed: {exc}")

st.subheader("EXPLAIN ANALYZE for a Single INSERT")
benchmark_target = st.selectbox("Choose an INSERT statement", ["transactions", "logs"])

if benchmark_target == "transactions":
    render_sql(TRANSACTION_INSERT_SQL)
else:
    render_sql(LOG_INSERT_SQL)

if st.button("Run INSERT EXPLAIN ANALYZE"):
    try:
        if benchmark_target == "transactions":
            plan_result = explain_analyze_rolled_back(TRANSACTION_INSERT_SQL, (1, 1, 250))
        else:
            plan_result = explain_analyze_rolled_back(LOG_INSERT_SQL, ("explain_demo_event",))

        summary = summarize_plan(plan_result)
        st.code(format_plan_summary(summary), language="text")
        with st.expander("Raw INSERT plan output"):
            st.code(json.dumps(plan_result, indent=2), language="json")
    except Exception as exc:
        st.error(f"INSERT EXPLAIN ANALYZE failed: {exc}")

render_internal_note(
    "Report alignment",
    """
    This page matches the report's high-frequency insert and concurrent read/write experiments more
    closely. The benchmark is still classroom-safe because all timed inserts are rolled back, but the
    measured work is real PostgreSQL execution work rather than simulated timing in Python.
    """,
)
