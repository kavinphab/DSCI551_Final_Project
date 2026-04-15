import streamlit as st

from db import query_df
from queries import AGGREGATION_SQL
from utils import render_dataframe, render_internal_note, render_sql


st.title("Aggregation Dashboard")
st.write("Compute the top 20 users by number of transactions.")

if st.button("Compute Top Users by Transaction Count"):
    try:
        df = query_df(AGGREGATION_SQL)
        st.success("Aggregation complete.")
        render_dataframe(df)
    except Exception as exc:
        st.error(f"Aggregation failed: {exc}")

st.subheader("SQL Used")
render_sql(AGGREGATION_SQL)

render_internal_note(
    "How this maps to PostgreSQL internals",
    """
    This is a large aggregation query, so the interesting internal behavior is often the grouping strategy.
    PostgreSQL may use `HashAggregate` or a sort-based alternative depending on cost and memory. Even if an
    index exists on `user_id`, the database still has to count many rows, so an index does not automatically
    make this query cheap.
    """,
)
