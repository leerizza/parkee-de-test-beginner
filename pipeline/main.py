"""Orchestrate extract (Postgres) -> load (ClickHouse raw), full-load, single tenant."""
import logging
import os
import time

from extract import TABLES, extract_all, get_pg_conn
from load import ensure_database, ensure_tables, full_load, get_ch_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("parkee_el")


def pg_config():
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", "5432"),
        "dbname": os.environ.get("POSTGRES_DB", "parkee_oltp"),
        "user": os.environ.get("POSTGRES_USER", "parkee"),
        "password": os.environ.get("POSTGRES_PASSWORD", "parkee"),
    }


def ch_config():
    return {
        "host": os.environ.get("CLICKHOUSE_HOST", "localhost"),
        "http_port": int(os.environ.get("CLICKHOUSE_HTTP_PORT", "8123")),
        "user": os.environ.get("CLICKHOUSE_USER", "parkee"),
        "password": os.environ.get("CLICKHOUSE_PASSWORD", "parkee"),
    }


def coerce_rows(table_name, columns, rows):
    """ClickHouse UInt8 expects int, not Python bool (products.is_active)."""
    if table_name == "products":
        idx = columns.index("is_active")
        rows = [
            row[:idx] + (int(row[idx]),) + row[idx + 1 :]
            for row in rows
        ]
    return rows


def main():
    start = time.time()
    log.info("Connecting to Postgres source...")
    pg_conn = get_pg_conn(pg_config())

    log.info("Connecting to ClickHouse (DWH)...")
    ch_client = get_ch_client(ch_config())
    ensure_database(ch_client, "raw")
    ensure_tables(ch_client)

    try:
        log.info("Extracting from Postgres: %s", ", ".join(TABLES))
        extracted = extract_all(pg_conn)

        total_rows = 0
        for table_name in TABLES:
            t0 = time.time()
            columns, rows = extracted[table_name]
            rows = coerce_rows(table_name, columns, rows)
            n = full_load(ch_client, table_name, columns, rows)
            elapsed = time.time() - t0
            total_rows += n
            log.info("Loaded raw.%s: %d rows in %.2fs", table_name, n, elapsed)

        log.info("EL pipeline complete: %d total rows in %.2fs", total_rows, time.time() - start)
    except Exception:
        log.exception("EL pipeline failed")
        raise
    finally:
        pg_conn.close()


if __name__ == "__main__":
    main()
