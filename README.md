# PostgreSQL Transaction Tracking and Activity Analytics Dashboard

## Project Overview

This project is a Streamlit application for a DSCI 551 course demo. It presents a single coherent business application for transaction tracking and analytics while explicitly connecting application behavior to PostgreSQL internals.

The dashboard uses PostgreSQL directly for all reads and writes. It does not generate mock data in Python.

## Architecture Summary

`Streamlit frontend -> Python application logic -> PostgreSQL`

- Streamlit handles the interface and user interactions.
- Python modules manage database access, reusable SQL helpers, and plan summaries.
- PostgreSQL performs storage, indexing, MVCC visibility, WAL logging, and query planning/execution internally.

## Schema Used

The app is built for this schema exactly:

```sql
users(
  id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT,
  created_at TIMESTAMP DEFAULT NOW()
)

assets(
  id SERIAL PRIMARY KEY,
  owner_id INT,
  asset_name TEXT,
  value INT,
  created_at TIMESTAMP DEFAULT NOW()
)

transactions(
  id SERIAL PRIMARY KEY,
  user_id INT,
  asset_id INT,
  amount INT,
  created_at TIMESTAMP
)

logs(
  id SERIAL PRIMARY KEY,
  event TEXT,
  created_at TIMESTAMP
)
```

Expected scale:

- `users`: 100,000 rows
- `assets`: 200,000 rows
- `transactions`: 500,000 rows
- `logs`: 100,000 rows

## Project Structure

```text
pg_txn_dashboard/
  app.py
  db.py
  init_db.py
  plan_utils.py
  queries.py
  utils.py
  pages/
    1_User_Transaction_Search.py
    2_Recent_Activity_Feed.py
    3_Joined_User_Transaction_View.py
    4_Aggregation_Dashboard.py
    5_Write_Update_Demo.py
    6_Database_Insights.py
    7_Admin_Setup.py
  requirements.txt
  .env.example
  README.md
```

## Code Structure

- app.py → main Streamlit entry point
- db.py → database connection and query execution
- init_db.py → schema creation and data generation
- plan_utils.py → EXPLAIN ANALYZE parsing
- queries.py → reusable SQL queries
- utils.py → helper functions
- pages/ → individual dashboard features

## Setup

1. Create and activate a Python virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
cd pg_txn_dashboard
pip install -r requirements.txt
```
All dependencies are listed in `requirements.txt`.

Key libraries:
- streamlit
- psycopg2 (or asyncpg)
- python-dotenv
  
3. Configure database credentials.

Option A: create a `.env` file from `.env.example` and set `DATABASE_URL`.

Option B: set PostgreSQL variables individually:

- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

You can also put the same values in Streamlit secrets.

4. Initialize the PostgreSQL database (run once).

```bash
python3 init_db.py
```
This script:
- Creates all required tables
- Inserts synthetic data into users, assets, transactions, and logs
- Simulates realistic relationships between tables

This creates the required tables and populates them with ~900k sample rows. Takes 5-10 minutes.

5. Start the Streamlit app.

```bash
streamlit run app.py
```

6. Navigate to the following pages:
   - User Transaction Search → test indexed vs non-indexed queries
   - Database Insights → view EXPLAIN ANALYZE output
   - Aggregation Dashboard → observe aggregation strategies

7. (Optional) Drop indexes and re-run:
   DROP INDEX idx_transactions_user_id;
   to observe sequential scan behavior.

6. Open the local Streamlit URL shown in the terminal.

## Page Summary

- `Home / Overview`: explains the dashboard, table relationships, project themes, and short comparisons with MySQL and MongoDB.
- `User Transaction Search`: retrieves transactions for one user and discusses heap access plus secondary B-tree indexes.
- `Recent Activity Feed`: shows the newest transactions for a user and highlights composite index behavior for filter plus sort.
- `Joined User Transaction View`: joins transactions with users and demonstrates join strategy selection.
- `Aggregation Dashboard`: computes top users by transaction count and discusses aggregation planning.
- `Write / Update Demo`: inserts log rows and updates asset values while explaining MVCC, tuple versioning, dead tuples, and write overhead.
- `Database Insights`: runs real `EXPLAIN ANALYZE` on the same app queries and summarizes what PostgreSQL actually executed.
- `Admin / Setup`: tests connectivity, checks whether demo indexes exist, and can create them for the class demo.

## Recommended Demo Indexes

The app can check or create these indexes:

```sql
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_user_created ON transactions(user_id, created_at DESC);
```

## Course Project Themes Covered

- PostgreSQL uses heap storage for table rows.
- PostgreSQL uses secondary B-tree indexes rather than clustered table organization like InnoDB.
- MVCC allows concurrent reads and writes through tuple versioning.
- The planner chooses scan, join, sort, and aggregate strategies based on cost.
- The application layer issues SQL, while PostgreSQL handles storage internals and execution decisions.

## Notes

- All SQL uses parameterized placeholders.
- The app connects directly to PostgreSQL and reads real data from the configured database.
- `Database Insights` uses real `EXPLAIN ANALYZE` output from PostgreSQL, not guessed plans.

## Environment Variables and Credentials

This project requires PostgreSQL credentials.

Do NOT commit credentials to GitHub.

Use either:
- a `.env` file (see `.env.example`)
- or environment variables

Required variables:
- DATABASE_URL OR
- PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

These are loaded in `db.py`.
