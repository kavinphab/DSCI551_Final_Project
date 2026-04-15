import streamlit as st

from db import query_df
from queries import USER_TRANSACTION_SQL
from utils import render_dataframe, render_internal_note, render_sql


st.title("User Transaction Search")
st.write("Enter a `user_id` to retrieve matching transactions directly from PostgreSQL.")

with st.form("user_transaction_search_form"):
    user_id = st.number_input("User ID", min_value=1, value=1, step=1)
    row_limit = st.number_input("Row limit", min_value=1, max_value=1000, value=25, step=1)
    submitted = st.form_submit_button("Search Transactions")

if submitted:
    try:
        df = query_df(USER_TRANSACTION_SQL, (int(user_id), int(row_limit)))
        st.success(f"Retrieved {len(df)} rows.")
        render_dataframe(df)
    except Exception as exc:
        st.error(f"Query failed: {exc}")

st.subheader("SQL Used")
render_sql(USER_TRANSACTION_SQL)

render_internal_note(
    "How this maps to PostgreSQL internals",
    """
    PostgreSQL stores table rows in heap pages. If there is no useful index, the database may need a
    sequential scan over the `transactions` heap to find rows for the target `user_id`. When a secondary
    B-tree index on `transactions(user_id)` exists, PostgreSQL can use the index to find matching tuple
    pointers and then fetch the visible rows from the heap.
    """,
)
