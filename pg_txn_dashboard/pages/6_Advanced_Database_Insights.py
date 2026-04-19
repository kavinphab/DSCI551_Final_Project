import streamlit as st

from queries import OPERATION_DETAILS
from utils import render_database_insights_panel, render_page_intro, render_workspace_sidebar


context = render_workspace_sidebar()
render_page_intro(
    "Advanced Query Planning Insights",
    "Use this page when you want a PostgreSQL-first view of the application workflows. It is a secondary deep-dive page, not the main entry point for normal use.",
    next_steps=[
        ("pages/2_Search_Explore_Transactions.py", "Return to main search workflow"),
        ("pages/4_Analytics_Summaries.py", "Return to analytics"),
    ],
)

operation_name = st.selectbox("Choose a workflow to inspect", list(OPERATION_DETAILS.keys()))
params = OPERATION_DETAILS[operation_name]["default_params"]

if operation_name in {"User Transaction Search", "Recent Activity Feed", "Joined User Transaction View"}:
    default_user_id = context["active_user_id"]
    user_id = st.number_input("User ID used for plan inspection", min_value=1, value=default_user_id, step=1)
    if operation_name == "User Transaction Search":
        row_limit = st.number_input("Row limit used for plan inspection", min_value=1, max_value=200, value=context["default_row_limit"], step=1)
        params = (int(user_id), int(row_limit))
    else:
        params = (int(user_id),)

render_database_insights_panel(operation_name, params, query_label=operation_name)
