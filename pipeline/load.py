"""Full-load raw data into ClickHouse (schema `raw`, truncate + insert)."""
import clickhouse_connect

RAW_DDL = {
    "customers": """
        CREATE TABLE IF NOT EXISTS raw.customers (
            customer_id Int32,
            name String,
            phone Nullable(String),
            email Nullable(String),
            gender Nullable(String),
            city Nullable(String),
            created_at DateTime
        ) ENGINE = MergeTree ORDER BY customer_id
    """,
    "products": """
        CREATE TABLE IF NOT EXISTS raw.products (
            product_id Int32,
            product_name String,
            category Nullable(String),
            brand Nullable(String),
            unit_price Decimal(12,2),
            is_active UInt8,
            created_at DateTime
        ) ENGINE = MergeTree ORDER BY product_id
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS raw.transactions (
            transaction_id Int32,
            customer_id Nullable(Int32),
            store_id Nullable(Int32),
            transaction_date DateTime,
            total_amount Decimal(14,2),
            payment_method Nullable(String),
            status String
        ) ENGINE = MergeTree ORDER BY transaction_id
    """,
    "transaction_items": """
        CREATE TABLE IF NOT EXISTS raw.transaction_items (
            item_id Int32,
            transaction_id Nullable(Int32),
            product_id Nullable(Int32),
            quantity Int32,
            unit_price Decimal(12,2),
            discount Decimal(5,2),
            subtotal Decimal(14,2)
        ) ENGINE = MergeTree ORDER BY item_id
    """,
}


def get_ch_client(cfg):
    return clickhouse_connect.get_client(
        host=cfg["host"],
        port=cfg["http_port"],
        username=cfg["user"],
        password=cfg["password"],
    )


def ensure_database(client, db_name):
    client.command(f"CREATE DATABASE IF NOT EXISTS {db_name}")


def ensure_tables(client):
    for ddl in RAW_DDL.values():
        client.command(ddl)


def full_load(client, table_name, columns, rows):
    """Truncate + insert: full-load, no incremental logic."""
    client.command(f"TRUNCATE TABLE IF EXISTS raw.{table_name}")
    if rows:
        client.insert(f"raw.{table_name}", rows, column_names=columns)
    return len(rows)
