# PostgreSQL Transaction Tracking and Activity Analytics Dashboard

This is a Streamlit course project for DSCI 551 focused on how PostgreSQL internals show up in application behavior.

The application is organized as one connected analyst workflow rather than a set of isolated demos: you can keep an active user and asset context in the sidebar, move from operational transaction views into planner analysis, and then validate the same workload through storage, MVCC, and write-overhead experiments.

## Architecture

`Streamlit frontend -> Python app logic -> PostgreSQL`

- Streamlit is the application layer and user interface.
- Python issues parameterized SQL and formats results.
- PostgreSQL handles heap storage, secondary B-tree indexes, MVCC visibility, WAL logging, and query planning/execution.

## What The App Covers

- Shared investigation workspace with active user and asset context carried across pages
- User transaction search with heap access and secondary index discussion
- Recent activity feed with composite index behavior
- Joined user/transaction view with planner-selected join strategy
- Aggregation dashboard with grouping strategy discussion
- Write/update demo with MVCC tuple-version explanation
- Database insights with real `EXPLAIN ANALYZE`
- Storage and MVCC evidence with `ctid`, `xmin`, `xmax`, dead tuples, and VACUUM
- Concurrent read/write MVCC snapshot demo
- Transaction insert benchmark showing write overhead with indexes

## Setup

1. Create a virtual environment and activate it.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Configure PostgreSQL credentials in `.env` or Streamlit secrets.

Example:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/dsci551_project
```

4. Initialize the schema and sample data if needed.

```bash
python3 init_db.py
```

5. Run the app.

```bash
streamlit run app.py
```

## Report Alignment

The app is designed to support the themes from the midterm report:

- Heap storage and non-clustered secondary indexes in PostgreSQL
- MVCC tuple versioning, dead tuples, and VACUUM cleanup
- Planner choices for scans, joins, sorting, aggregation, and insert work
- High-level WAL and index-maintenance write overhead
- Concise comparisons with MySQL/InnoDB and MongoDB

## Cohesive Platform Improvements

- Persistent sidebar workspace so the same user and asset can be analyzed across the whole app
- Guided workflow on the home page and per-page next-step navigation
- Operational pages first, then internal evidence pages, mirroring a real analyst investigation flow
- Live active-user snapshot in the sidebar to reduce repetitive lookups and keep context visible

## Notes

- The concurrency and insert benchmark pages use real database work but keep the demo safe by rolling back benchmark inserts where appropriate.
- The bulk asset update experiment is intentionally committed so that you can observe dead tuples and then run `VACUUM ANALYZE`.
