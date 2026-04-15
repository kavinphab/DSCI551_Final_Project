import pandas as pd
import streamlit as st

from db import execute_write, fetch_one
from queries import GET_ASSET_SQL, INSERT_LOG_SQL, UPDATE_ASSET_SQL
from utils import render_dataframe, render_internal_note, render_sql


st.title("Write / Update Demo")
st.write("This page performs controlled writes so the demo includes real insert and update behavior.")

tab1, tab2 = st.tabs(["Insert Log Entry", "Update Asset Value"])

with tab1:
    with st.form("insert_log_form"):
        event = st.text_input("Log event", value="Demo activity from Streamlit dashboard")
        insert_submitted = st.form_submit_button("Insert Log Entry")

    if insert_submitted:
        if not event.strip():
            st.error("Please enter a non-empty log event.")
        else:
            try:
                rows, rowcount = execute_write(INSERT_LOG_SQL, (event.strip(),))
                st.success(f"Inserted {rowcount} row.")
                render_dataframe(pd.DataFrame(rows))
            except Exception as exc:
                st.error(f"Insert failed: {exc}")

    st.markdown("**SQL Used**")
    render_sql(INSERT_LOG_SQL)

with tab2:
    with st.form("update_asset_form"):
        asset_id = st.number_input("Asset ID", min_value=1, value=1, step=1)
        new_value = st.number_input("New asset value", value=100, step=1)
        update_submitted = st.form_submit_button("Update Asset Value")

    if update_submitted:
        try:
            before_row = fetch_one(GET_ASSET_SQL, (int(asset_id),))
            if before_row is None:
                st.error("Asset not found.")
            else:
                updated_rows, rowcount = execute_write(UPDATE_ASSET_SQL, (int(new_value), int(asset_id)))
                after_row = updated_rows[0] if updated_rows else None

                st.success(f"Updated {rowcount} row.")
                st.markdown("**Before / After**")
                comparison_df = pd.DataFrame(
                    [
                        {"state": "before", **before_row},
                        {"state": "after", **after_row},
                    ]
                )
                render_dataframe(comparison_df)
        except Exception as exc:
            st.error(f"Update failed: {exc}")

    st.markdown("**SQL Used**")
    render_sql(UPDATE_ASSET_SQL)

render_internal_note(
    "How this maps to PostgreSQL internals",
    """
    PostgreSQL uses MVCC, so an `UPDATE` creates a new row version instead of overwriting the old tuple in
    place. That means writes can leave dead tuples behind until vacuum cleans them up. Inserts and updates
    also generate WAL records and may require index maintenance, which is part of the write overhead the
    database manages internally.
    """,
)
