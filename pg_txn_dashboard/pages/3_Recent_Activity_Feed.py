import streamlit as st

from db import query_df
from queries import RECENT_ACTIVITY_SQL
from utils import (
    render_custom_database_insights_panel,
    render_internal_note,
    render_page_intro,
    render_workspace_sidebar,
    update_workspace_context,
)


context = render_workspace_sidebar()
render_page_intro(
    "Recent Activity Feed",
    "Review the latest transaction events for the active user in a feed-style view, then expand the insights section to see how PostgreSQL handles the filter and sort.",
    next_steps=[
        ("pages/2_Search_Explore_Transactions.py", "Back to search"),
        ("pages/4_Analytics_Summaries.py", "Open analytics"),
    ],
)

with st.form("recent_activity_feed_form"):
    user_id = st.number_input("User ID", min_value=1, value=context["active_user_id"], step=1)
    submitted = st.form_submit_button("Load Activity Feed")

if submitted:
    update_workspace_context(user_id=int(user_id))
    try:
        activity = query_df(RECENT_ACTIVITY_SQL, (int(user_id),))
        st.success(f"Loaded {len(activity)} recent transactions.")

        if activity.empty:
            st.info("No recent transactions were found for this user.")
        else:
            for row in activity.to_dict("records"):
                with st.container(border=True):
                    top_left, top_right = st.columns([3, 1])
                    top_left.markdown(f"**Transaction #{row['id']}**")
                    top_left.caption(f"Asset {row['asset_id']} · User {row['user_id']}")
                    top_right.metric("Amount", f"{row['amount']}")
                    st.caption(f"Created at: {row['created_at']}")

        with st.expander("Database Insights", expanded=False):
            render_custom_database_insights_panel(
                RECENT_ACTIVITY_SQL,
                (int(user_id),),
                (
                    "This activity feed combines a selective `WHERE user_id = ...` filter with descending time order. "
                    "The composite index on `(user_id, created_at DESC)` is designed for exactly this feed pattern."
                ),
                "recent activity feed",
            )
    except Exception as exc:
        st.error(f"Could not load activity feed: {exc}")

render_internal_note(
    "Audit-trail interpretation",
    """
    This page is intentionally framed like a lightweight activity timeline. The internals explanation stays secondary,
    so the user can first read it as an operational feed and only then inspect the query behavior underneath.
    """,
)
