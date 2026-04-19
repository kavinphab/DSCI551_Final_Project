import streamlit as st

from db import get_platform_overview
from queries import OPERATION_DETAILS
from utils import render_workflow_panel, render_workspace_sidebar


st.set_page_config(
    page_title="PostgreSQL Transaction Tracking Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

context = render_workspace_sidebar()

st.title("PostgreSQL Transaction Tracking and Activity Analytics Dashboard")
st.write(
    """
    This Streamlit application is a single analyst workspace for investigating user activity,
    transaction flows, write behavior, and PostgreSQL internals in one connected platform.
    The same active user and asset context can follow you from operational views into
    query plans, MVCC evidence, and write-overhead analysis.
    """
)

try:
    overview = get_platform_overview()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total users", f"{int(overview.get('total_users') or 0):,}")
    col2.metric("Total assets", f"{int(overview.get('total_assets') or 0):,}")
    col3.metric("Total transactions", f"{int(overview.get('total_transactions') or 0):,}")
    col4.metric("Total logs", f"{int(overview.get('total_logs') or 0):,}")
except Exception:
    st.info("Connect the database to load live platform overview metrics.")

st.subheader("Current Investigation Context")
st.markdown(
    f"""
    - Active user: `{context['active_user_id']}`
    - Active asset: `{context['active_asset_id']}`
    - Default row limit: `{context['default_row_limit']}`
    """
)

st.subheader("Main Workflows")
col1, col2 = st.columns(2)
with col1:
    render_workflow_panel(
        "Search & Explore Transactions",
        "Search a user, inspect their transactions, and optionally expand the result into a richer joined view with user and asset details.",
        "pages/2_Search_Explore_Transactions.py",
        "Open transaction search",
    )
    render_workflow_panel(
        "Analytics & Summaries",
        "View platform-wide patterns such as the users generating the most transaction volume.",
        "pages/4_Analytics_Summaries.py",
        "Open analytics",
    )
with col2:
    render_workflow_panel(
        "Recent Activity Feed",
        "Follow a user's most recent transaction events in a feed-style operational view.",
        "pages/3_Recent_Activity_Feed.py",
        "Open activity feed",
    )
    render_workflow_panel(
        "Update & Record Activity",
        "Insert a log entry or update an asset value to make the application feel like a live internal system.",
        "pages/5_Update_Record_Activity.py",
        "Open update workflow",
    )

st.subheader("Advanced Evidence")
advanced_cols = st.columns(3)
advanced_cols[0].page_link("pages/6_Advanced_Database_Insights.py", label="Advanced query planning")
advanced_cols[1].page_link("pages/7_Storage_MVCC_Evidence.py", label="Storage & MVCC evidence")
advanced_cols[2].page_link("pages/8_Concurrency_and_Insert_Benchmark.py", label="Concurrency & write behavior")

st.subheader("Application Relationships")
st.code(
    """users.id -> transactions.user_id
assets.id -> transactions.asset_id
users.id -> assets.owner_id""",
    language="text",
)

st.subheader("How To Use This Demo")
st.markdown(
    """
    - Use the shared sidebar to keep one active user and asset across the whole app.
    - Start with user-facing operational pages, then move into internal analysis pages.
    - The `Database Insights` page runs `EXPLAIN ANALYZE` on the same queries used by the app.
    - The `Storage and MVCC Evidence` page shows tuple-version changes, dead tuples, and VACUUM effects.
    - The `Concurrency and Insert Benchmark` page demonstrates snapshot isolation and write overhead.
    - The `Admin / Setup` page can verify connectivity and create demo indexes if needed.
    """
)

st.subheader("Application Operations and PostgreSQL Internals")
for name, details in OPERATION_DETAILS.items():
    st.markdown(f"**{name}**")
    st.markdown(f"- Application operation: {details['business_summary']}")
    st.markdown(f"- Internal concept: {details['internal_focus']}")

st.subheader("Course Project Themes")
st.markdown(
    """
    - PostgreSQL stores table rows in heap files, so row retrieval often means reading heap tuples.
    - PostgreSQL uses secondary B-tree indexes, which point to heap tuples instead of organizing the
      whole table as a clustered primary-key structure.
    - MVCC supports concurrent reads and writes by keeping tuple versions rather than overwriting rows
      in place.
    - The planner chooses scan, join, sort, and aggregation strategies based on cost estimates and the
      available indexes.
    - The Streamlit app is the application layer; PostgreSQL is the system that actually handles storage,
      indexing, visibility rules, WAL, and execution.
    """
)

st.subheader("Midterm Report Coverage")
st.markdown(
    """
    - Storage and MVCC: tuple-version demo with `ctid`, `xmin`, `xmax`, plus dead tuple and VACUUM evidence.
    - Indexing: single-column and composite B-tree index behavior on `transactions`.
    - Query planning and execution: actual `EXPLAIN ANALYZE` output for filters, joins, sorting, aggregation, and inserts.
    - Concurrency: two-session MVCC snapshot demo showing that readers are not blocked by writers.
    - Write overhead: rollback-based insert benchmark centered on `transactions` so you can compare heavier indexed writes against lighter inserts.
    """
)

st.subheader("Short Comparison")
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        **PostgreSQL vs MySQL (InnoDB)**

        PostgreSQL uses heap storage plus secondary indexes, so an index lookup commonly leads to a
        separate heap fetch. InnoDB is clustered around the primary key, so the table itself is organized
        by primary-key order at a high level.
        """
    )

with col2:
    st.markdown(
        """
        **PostgreSQL vs MongoDB**

        PostgreSQL is a relational row-store built around tables, joins, and SQL planning. MongoDB is
        document-oriented and stores flexible JSON-like documents instead of normalized relational rows.
        """
    )

st.info(
    "For best results, configure the database connection in `.env` or Streamlit secrets before opening the query pages."
)
