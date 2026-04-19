import streamlit as st

from db import create_index, index_exists, test_connection
from queries import INDEX_DEFINITIONS
from utils import render_page_intro, render_workspace_sidebar


render_workspace_sidebar()
render_page_intro(
    "Admin / Setup",
    "Configure the platform, verify connectivity, and keep the recommended indexes in place so the operational and internal-analysis pages stay connected.",
)
st.warning("This page is for demo and setup purposes only. Do not use it as a production admin console.")

st.subheader("Initial Database Setup")
st.markdown("""
### Step 1: Configure Database Credentials
1. Create a `.env` file in the `pg_txn_dashboard/` directory
2. Add your PostgreSQL connection details:
   ```
   DATABASE_URL=postgresql://kavinphabiani@localhost:5432/dsci551_project
   ```
   Or set individual variables:
   ```
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=dsci551_project
   PGUSER=kavinphabiani
   ```

### Step 2: Initialize Database
Run this command once to create tables and populate sample data:
```bash
python3 init_db.py
```

This will:
- Create 4 tables: users, assets, transactions, logs
- Insert 100,000 users
- Insert 200,000 assets
- Insert 500,000 transactions
- Insert 100,000 logs

(Takes 5-10 minutes on most machines)

### Step 3: Verify Connection
Once initialized, use the button below to test the connection.
""")

if st.button("Test Database Connection"):
    ok, message = test_connection()
    if ok:
        st.success(message)
    else:
        st.error(message)

st.subheader("Demo Index Status")
try:
    status_rows = []
    for index_name in INDEX_DEFINITIONS:
        status_rows.append({"index_name": index_name, "exists": index_exists(index_name)})
    st.dataframe(status_rows, use_container_width=True, hide_index=True)
except Exception as exc:
    st.error(f"Could not inspect indexes yet: {exc}")

st.subheader("Create Recommended Demo Indexes")
for index_name, index_sql in INDEX_DEFINITIONS.items():
    if st.button(f"Create {index_name}"):
        try:
            create_index(index_sql)
            st.success(f"Index `{index_name}` is ready.")
        except Exception as exc:
            st.error(f"Failed to create `{index_name}`: {exc}")

st.markdown(
    """
    **Recommended indexes**

    - `CREATE INDEX idx_transactions_user_id ON transactions(user_id);`
    - `CREATE INDEX idx_transactions_user_created ON transactions(user_id, created_at DESC);`
    """
)
