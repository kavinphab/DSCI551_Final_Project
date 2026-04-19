import streamlit as st

from db import query_df
from queries import (
    USER_TRANSACTION_JOINED_SQL,
    USER_TRANSACTION_JOINED_SQL_ASC,
    USER_TRANSACTION_SQL,
    USER_TRANSACTION_SQL_ASC,
)
from utils import (
    render_custom_database_insights_panel,
    render_dataframe,
    render_internal_note,
    render_page_intro,
    render_workspace_sidebar,
    update_workspace_context,
)


context = render_workspace_sidebar()
render_page_intro(
    "Search & Explore Transactions",
    "Search transactions for a specific user, switch between operational and enriched views, and expand the embedded database insights only when you want the PostgreSQL explanation.",
    next_steps=[
        ("pages/3_Recent_Activity_Feed.py", "Open recent activity"),
        ("pages/4_Analytics_Summaries.py", "Open analytics"),
        ("pages/5_Update_Record_Activity.py", "Record activity"),
    ],
)

with st.form("search_explore_transactions_form"):
    col1, col2, col3 = st.columns(3)
    user_id = col1.number_input("User ID", min_value=1, value=context["active_user_id"], step=1)
    row_limit = col2.number_input("Row limit", min_value=1, max_value=1000, value=context["default_row_limit"], step=1)
    sort_order = col3.selectbox("Date order", ["Newest first", "Oldest first"], index=0)

    joined_view = st.toggle("Include user and asset details", value=True)
    submitted = st.form_submit_button("Search Transactions")

if submitted:
    update_workspace_context(user_id=int(user_id), row_limit=int(row_limit))

    if joined_view and sort_order == "Newest first":
        sql = USER_TRANSACTION_JOINED_SQL
        explanation = (
            "This enriched search still starts from transactions, but PostgreSQL must also plan the joins to users "
            "and assets. With a selective `user_id` filter, the planner can often narrow the transaction rows first "
            "and then join the smaller result to related tables."
        )
        insight_label = "search with joined user + asset context"
    elif joined_view:
        sql = USER_TRANSACTION_JOINED_SQL_ASC
        explanation = (
            "The joins are the same as the joined search, but the sort direction changes the access and ordering work. "
            "If the existing composite index is descending on `created_at`, PostgreSQL may need extra work to produce the oldest rows first."
        )
        insight_label = "search with joined user + asset context"
    elif sort_order == "Newest first":
        sql = USER_TRANSACTION_SQL
        explanation = (
            "This search filters on `user_id` and sorts by newest transaction time. PostgreSQL can use a secondary "
            "B-tree index to narrow matching tuple pointers, then read the visible heap rows for the result."
        )
        insight_label = "transaction search"
    else:
        sql = USER_TRANSACTION_SQL_ASC
        explanation = (
            "The same user filter applies here, but oldest-first ordering can change whether PostgreSQL can fully rely "
            "on the preferred index ordering or needs more work to return the requested sort direction."
        )
        insight_label = "transaction search"

    try:
        results = query_df(sql, (int(user_id), int(row_limit)))
        st.success(f"Loaded {len(results)} transactions for user {int(user_id)}.")
        render_dataframe(results)
        with st.expander("Database Insights", expanded=False):
            render_custom_database_insights_panel(sql, (int(user_id), int(row_limit)), explanation, insight_label)
    except Exception as exc:
        st.error(f"Search failed: {exc}")

render_internal_note(
    "Why this workflow feels more integrated",
    """
    This page starts with a business task: investigate one user's transactions. The database details stay available
    in the same workflow through the embedded insights panel instead of forcing a jump to a separate diagnostics page.
    """,
)
