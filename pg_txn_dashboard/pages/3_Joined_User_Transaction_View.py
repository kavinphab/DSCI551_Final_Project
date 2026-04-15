import streamlit as st

from db import query_df
from queries import JOINED_USER_TRANSACTION_SQL
from utils import render_dataframe, render_internal_note, render_sql


st.title("Joined User Transaction View")
st.write("Combine transaction rows with user profile information for a richer dashboard view.")

with st.form("joined_user_transaction_form"):
    user_id = st.number_input("User ID", min_value=1, value=1, step=1)
    submitted = st.form_submit_button("Load Joined Results")

if submitted:
    try:
        df = query_df(JOINED_USER_TRANSACTION_SQL, (int(user_id),))
        st.success(f"Retrieved {len(df)} rows.")
        render_dataframe(df)
    except Exception as exc:
        st.error(f"Query failed: {exc}")

st.subheader("SQL Used")
render_sql(JOINED_USER_TRANSACTION_SQL)

render_internal_note(
    "How this maps to PostgreSQL internals",
    """
    PostgreSQL's planner chooses a join strategy based on cost estimates. For a selective lookup on one
    `user_id`, the planner may choose a nested loop with a small set of matching rows, or another strategy
    such as a hash join if it estimates that hashing is cheaper. The app exposes that choice in the
    `Database Insights` page with real `EXPLAIN ANALYZE` output.
    """,
)
