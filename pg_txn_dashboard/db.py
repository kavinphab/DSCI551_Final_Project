import os
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
