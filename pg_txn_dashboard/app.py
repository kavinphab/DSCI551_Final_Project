import streamlit as st

from queries import OPERATION_DETAILS


st.set_page_config(
    page_title="PostgreSQL Transaction Tracking Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)


st.title("PostgreSQL Transaction Tracking and Activity Analytics Dashboard")
st.write(
    """
    This Streamlit application is a single business-facing dashboard for tracking user
    transactions, recent activity, joins, aggregation, and controlled writes on top of a
    PostgreSQL database. The goal is to show how application behavior maps directly to
    PostgreSQL internals such as heap storage, secondary B-tree indexes, MVCC, query
    planning, and write overhead.
    """
)

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
    - Use the pages in the left sidebar to explore read queries, joins, analytics, and writes.
    - The `Database Insights` page runs `EXPLAIN ANALYZE` on the same queries used by the app.
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
