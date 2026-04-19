import streamlit as st

from db import get_platform_overview, query_df
from queries import AGGREGATION_WITH_USER_SQL
from utils import (
    render_custom_database_insights_panel,
    render_dataframe,
    render_internal_note,
    render_page_intro,
    render_workspace_sidebar,
)


render_workspace_sidebar()
render_page_intro(
    "Analytics & Summaries",
    "Step back from one-user investigation and view the broader transaction system through top-user rankings and platform-level summary metrics.",
    next_steps=[
        ("pages/2_Search_Explore_Transactions.py", "Investigate a user"),
        ("pages/5_Update_Record_Activity.py", "Record a change"),
    ],
)

try:
    overview = get_platform_overview()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Users", f"{int(overview.get('est_users') or 0):,}")
    col2.metric("Assets", f"{int(overview.get('est_assets') or 0):,}")
    col3.metric("Transactions", f"{int(overview.get('est_transactions') or 0):,}")
    col4.metric("Logs", f"{int(overview.get('est_logs') or 0):,}")
except Exception as exc:
    st.info(f"Could not load overview metrics: {exc}")

if st.button("Refresh Top Users by Transaction Count"):
    try:
        analytics = query_df(AGGREGATION_WITH_USER_SQL)
        render_dataframe(analytics)

        if not analytics.empty:
            chart_df = analytics.set_index("name")[["txn_count"]]
            st.bar_chart(chart_df)

        with st.expander("Database Insights", expanded=False):
            render_custom_database_insights_panel(
                AGGREGATION_WITH_USER_SQL,
                (),
                (
                    "PostgreSQL still has to inspect a large portion of the transactions table to compute these counts. "
                    "The interesting planner decision is usually how it groups and orders the results, such as HashAggregate "
                    "versus sort-based aggregation."
                ),
                "analytics aggregation",
            )
    except Exception as exc:
        st.error(f"Analytics query failed: {exc}")

render_internal_note(
    "Why this is an analytics workflow, not a SQL demo",
    """
    The page foregrounds a business question first: who drives the most transaction volume? The SQL grouping logic and
    plan details are still present, but only as an embedded explanation under the analytics output.
    """,
)
