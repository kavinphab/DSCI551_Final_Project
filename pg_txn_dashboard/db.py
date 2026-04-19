import os
import time
from contextlib import contextmanager
from typing import Any, Iterable

import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv()


def _get_secret_or_env(key: str, default: str | None = None) -> str | None:
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)


def get_connection_kwargs() -> dict[str, Any]:
    db_url = _get_secret_or_env("DATABASE_URL")
    if db_url:
        return {"conninfo": db_url}

    return {
        "host": _get_secret_or_env("PGHOST", "localhost"),
        "port": int(_get_secret_or_env("PGPORT", "5432")),
        "dbname": _get_secret_or_env("PGDATABASE"),
        "user": _get_secret_or_env("PGUSER"),
        "password": _get_secret_or_env("PGPASSWORD"),
    }


@contextmanager
def get_connection():
    kwargs = get_connection_kwargs()
    conn = psycopg.connect(**kwargs)
    try:
        yield conn
    finally:
        conn.close()


def test_connection() -> tuple[bool, str]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user, version();")
                db_name, db_user, version = cur.fetchone()
        return True, f"Connected to database `{db_name}` as `{db_user}`. Server: {version}"
    except Exception as exc:
        return False, str(exc)


def query_df(sql: str, params: Iterable[Any] | None = None) -> pd.DataFrame:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
    return pd.DataFrame(rows)


def fetch_one(sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()


def execute_write(sql: str, params: Iterable[Any] | None = None) -> tuple[list[dict[str, Any]], int]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall() if cur.description else []
            rowcount = cur.rowcount
        conn.commit()
    return rows, rowcount


def explain_analyze(sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) {sql}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(explain_sql, params or ())
            result = cur.fetchone()
    return result[0]


def index_exists(index_name: str) -> bool:
    sql = """
    SELECT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = current_schema()
          AND indexname = %s
    ) AS exists;
    """
    row = fetch_one(sql, (index_name,))
    return bool(row and row["exists"])


def create_index(index_sql: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(index_sql)
        conn.commit()


def execute_statement(sql: str, params: Iterable[Any] | None = None, autocommit: bool = True) -> None:
    with get_connection() as conn:
        if autocommit:
            conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        if not autocommit:
            conn.commit()


def fetch_many(sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()


def get_table_storage_stats(table_name: str) -> dict[str, Any] | None:
    sql = """
    SELECT
        stats.relname AS table_name,
        stats.n_live_tup,
        stats.n_dead_tup,
        stats.seq_scan,
        stats.idx_scan,
        stats.last_vacuum,
        stats.last_autovacuum,
        stats.last_analyze,
        stats.last_autoanalyze,
        pg_size_pretty(pg_table_size(stats.relid)) AS heap_size,
        pg_size_pretty(pg_indexes_size(stats.relid)) AS indexes_size,
        pg_size_pretty(pg_total_relation_size(stats.relid)) AS total_size
    FROM pg_stat_user_tables AS stats
    WHERE stats.relname = %s;
    """
    return fetch_one(sql, (table_name,))


def get_table_indexes(table_name: str) -> list[dict[str, Any]]:
    sql = """
    SELECT
        indexname,
        indexdef
    FROM pg_indexes
    WHERE schemaname = current_schema()
      AND tablename = %s
    ORDER BY indexname;
    """
    return fetch_many(sql, (table_name,))


def run_mvcc_tuple_demo(user_id: int) -> dict[str, Any]:
    before_sql = """
    SELECT id, name, email, ctid::text AS ctid, xmin::text AS xmin, xmax::text AS xmax
    FROM users
    WHERE id = %s;
    """
    update_sql = """
    UPDATE users
    SET name = %s
    WHERE id = %s
    RETURNING id, name, email, ctid::text AS ctid, xmin::text AS xmin, xmax::text AS xmax;
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(before_sql, (user_id,))
            before_row = cur.fetchone()
            if before_row is None:
                conn.rollback()
                return {"before": None, "after": None}

            updated_name = f"{before_row['name']}_mvcc_demo"
            cur.execute(update_sql, (updated_name, user_id))
            after_row = cur.fetchone()
        conn.rollback()

    return {"before": before_row, "after": after_row}


def run_bulk_asset_update(asset_start_id: int, row_count: int, delta: int) -> dict[str, Any]:
    before_stats = get_table_storage_stats("assets")
    update_sql = """
    UPDATE assets
    SET value = value + %s
    WHERE id BETWEEN %s AND %s;
    """
    upper_id = asset_start_id + row_count - 1

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(update_sql, (delta, asset_start_id, upper_id))
            affected_rows = cur.rowcount
        conn.commit()

    execute_statement("ANALYZE assets;")
    after_stats = get_table_storage_stats("assets")
    return {
        "affected_rows": affected_rows,
        "before_stats": before_stats,
        "after_stats": after_stats,
        "start_id": asset_start_id,
        "end_id": upper_id,
        "delta": delta,
    }


def vacuum_analyze_table(table_name: str) -> None:
    execute_statement(f"VACUUM (VERBOSE, ANALYZE) {table_name};")


def run_concurrent_mvcc_demo(user_id: int, asset_id: int = 1, amount: int = 777) -> dict[str, Any]:
    insert_sql = """
    INSERT INTO transactions (user_id, asset_id, amount, created_at)
    VALUES (%s, %s, %s, NOW())
    RETURNING id;
    """
    count_sql = "SELECT COUNT(*) AS txn_count FROM transactions WHERE user_id = %s;"
    delete_sql = "DELETE FROM transactions WHERE id = %s;"

    conn_a = psycopg.connect(**get_connection_kwargs())
    conn_b = psycopg.connect(**get_connection_kwargs())
    cleanup_conn = psycopg.connect(**get_connection_kwargs())

    inserted_id = None
    try:
        conn_a.execute("BEGIN ISOLATION LEVEL REPEATABLE READ;")
        with conn_a.cursor(row_factory=dict_row) as cur_a:
            cur_a.execute(count_sql, (user_id,))
            count_before = cur_a.fetchone()["txn_count"]

        conn_b.execute("BEGIN;")
        with conn_b.cursor(row_factory=dict_row) as cur_b:
            cur_b.execute(insert_sql, (user_id, asset_id, amount))
            inserted_id = cur_b.fetchone()["id"]
        conn_b.commit()

        with conn_a.cursor(row_factory=dict_row) as cur_a:
            cur_a.execute(count_sql, (user_id,))
            count_during = cur_a.fetchone()["txn_count"]
        conn_a.commit()

        with cleanup_conn.cursor(row_factory=dict_row) as cur_cleanup:
            cur_cleanup.execute(count_sql, (user_id,))
            count_after_commit = cur_cleanup.fetchone()["txn_count"]
            cur_cleanup.execute(delete_sql, (inserted_id,))
        cleanup_conn.commit()

        return {
            "user_id": user_id,
            "inserted_transaction_id": inserted_id,
            "count_before": count_before,
            "count_during_repeatable_read": count_during,
            "count_after_commit": count_after_commit,
        }
    finally:
        if inserted_id is not None and not cleanup_conn.closed:
            try:
                with cleanup_conn.cursor() as cur_cleanup:
                    cur_cleanup.execute(delete_sql, (inserted_id,))
                cleanup_conn.commit()
            except Exception:
                cleanup_conn.rollback()
        for conn in (conn_a, conn_b, cleanup_conn):
            if not conn.closed:
                conn.close()


def benchmark_insert_batches(batch_size: int, sample_user_id: int = 1, sample_asset_id: int = 1) -> dict[str, Any]:
    transaction_rows = [
        (sample_user_id, sample_asset_id, 100 + (i % 10),)
        for i in range(batch_size)
    ]
    log_rows = [
        (f"benchmark_event_{i}",)
        for i in range(batch_size)
    ]

    txn_sql = """
    INSERT INTO transactions (user_id, asset_id, amount, created_at)
    VALUES (%s, %s, %s, NOW());
    """
    log_sql = """
    INSERT INTO logs (event, created_at)
    VALUES (%s, NOW());
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            start = time.perf_counter()
            cur.executemany(txn_sql, transaction_rows)
            transaction_elapsed_ms = (time.perf_counter() - start) * 1000
        conn.rollback()

    with get_connection() as conn:
        with conn.cursor() as cur:
            start = time.perf_counter()
            cur.executemany(log_sql, log_rows)
            log_elapsed_ms = (time.perf_counter() - start) * 1000
        conn.rollback()

    return {
        "batch_size": batch_size,
        "transactions_elapsed_ms": transaction_elapsed_ms,
        "logs_elapsed_ms": log_elapsed_ms,
        "transactions_indexes": get_table_indexes("transactions"),
        "logs_indexes": get_table_indexes("logs"),
    }


def explain_analyze_rolled_back(sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) {sql}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(explain_sql, params or ())
            result = cur.fetchone()
        conn.rollback()
    return result[0]


def get_user_workspace_summary(user_id: int) -> dict[str, Any] | None:
    sql = """
    SELECT
        u.id,
        u.name,
        u.email,
        (
            SELECT COUNT(*)
            FROM assets a
            WHERE a.owner_id = u.id
        ) AS asset_count,
        (
            SELECT COUNT(*)
            FROM transactions t
            WHERE t.user_id = u.id
        ) AS txn_count,
        (
            SELECT MAX(t.created_at)
            FROM transactions t
            WHERE t.user_id = u.id
        ) AS last_transaction_at
    FROM users u
    WHERE u.id = %s;
    """
    return fetch_one(sql, (user_id,))


def get_platform_overview() -> dict[str, Any]:
    sql = """
    SELECT
        (SELECT COUNT(*) FROM users) AS total_users,
        (SELECT COUNT(*) FROM assets) AS total_assets,
        (SELECT COUNT(*) FROM transactions) AS total_transactions,
        (SELECT COUNT(*) FROM logs) AS total_logs;
    """
    overview = fetch_one(sql) or {}
    latest_txn = fetch_one("SELECT MAX(created_at) AS latest_transaction_at FROM transactions;")
    latest_log = fetch_one("SELECT MAX(created_at) AS latest_log_at FROM logs;")
    overview["latest_transaction_at"] = latest_txn["latest_transaction_at"] if latest_txn else None
    overview["latest_log_at"] = latest_log["latest_log_at"] if latest_log else None
    return overview
