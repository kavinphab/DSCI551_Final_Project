# PostgreSQL Transaction Tracking and Activity Analytics Dashboard

This is a Streamlit course project for DSCI 551 focused on how PostgreSQL internals show up in application behavior.

## Architecture

`Streamlit frontend -> Python app logic -> PostgreSQL`

- Streamlit is the application layer and user interface.
- Python issues parameterized SQL and formats results.
- PostgreSQL handles heap storage, secondary B-tree indexes, MVCC visibility, WAL logging, and query planning/execution.

## What The App Covers

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

## Notes

- The concurrency and insert benchmark pages use real database work but keep the demo safe by rolling back benchmark inserts where appropriate.
- The bulk asset update experiment is intentionally committed so that you can observe dead tuples and then run `VACUUM ANALYZE`.
