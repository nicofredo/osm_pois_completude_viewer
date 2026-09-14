"""
db.py

Low-level, shared database helpers used by both the creation and update
pipelines (and occasionally by export). Keeps the psycopg connection
boilerplate and schema-level setup in one place.
"""

import psycopg

from config import pg_connection_kwargs


def get_connection(autocommit: bool = False) -> psycopg.Connection:
    """Open a new psycopg connection using the shared config."""
    conn = psycopg.connect(**pg_connection_kwargs())
    conn.autocommit = autocommit
    return conn


def create_postgis_if_not_exists() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")


def create_schema_if_not_exists(schema_name: str) -> None:
    conn = get_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(
                psycopg.sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    psycopg.sql.Identifier(schema_name)
                )
            )
    finally:
        conn.close()
