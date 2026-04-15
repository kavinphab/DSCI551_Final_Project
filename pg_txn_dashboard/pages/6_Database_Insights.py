import streamlit as st

from queries import OPERATION_DETAILS
from utils import render_explain_section


st.title("Database Insights")
st.write(
    "Run `EXPLAIN ANALYZE` on the same queries used by the application and inspect what PostgreSQL actually chose."
)

operation_name = st.selectbox("Choose an operation", list(OPERATION_DETAILS.keys()))
details = OPERATION_DETAILS[operation_name]

st.markdown("**Operation focus**")
st.write(details["internal_focus"])

params = details["default_params"]

if operation_name in {"User Transaction Search", "Recent Activity Feed", "Joined User Transaction View"}:
    default_user_id = int(params[0]) if params else 1
    safe_user_id = st.number_input("User ID used for EXPLAIN ANALYZE", min_value=1, value=default_user_id, step=1)
    if operation_name == "User Transaction Search":
        default_limit = int(params[1])
        safe_limit = st.number_input("Row limit used for EXPLAIN ANALYZE", min_value=1, max_value=200, value=default_limit, step=1)
        params = (int(safe_user_id), int(safe_limit))
    else:
        params = (int(safe_user_id),)

if st.button("Run EXPLAIN ANALYZE"):
    try:
        render_explain_section(operation_name, params)
    except Exception as exc:
        st.error(f"EXPLAIN ANALYZE failed: {exc}")
