import streamlit as st

from db import query_df
from queries import RECENT_ACTIVITY_SQL
from utils import render_dataframe, render_internal_note, render_sql


st.title("Recent Activity Feed")
st.write("Show the 20 newest transactions for one user.")

with st.form("recent_activity_form"):
    user_id = st.number_input("User ID", min_value=1, value=1, step=1)
    submitted = st.form_submit_button("Load Recent Activity")

if submitted:
    try:
        df = query_df(RECENT_ACTIVITY_SQL, (int(user_id),))
        st.success(f"Retrieved {len(df)} rows.")
        render_dataframe(df)
    except Exception as exc:
        st.error(f"Query failed: {exc}")

st.subheader("SQL Used")
render_sql(RECENT_ACTIVITY_SQL)

render_internal_note(
    "How this maps to PostgreSQL internals",
    """
    This pattern combines filtering and sorting. A composite index on
    `transactions(user_id, created_at DESC)` can let PostgreSQL satisfy both the `WHERE` clause and the
    descending `ORDER BY` from the index access path. That reduces extra sorting work and helps the app
    fetch recent activity efficiently.
    """,
)
