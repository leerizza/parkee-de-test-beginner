"""Extract data from the Postgres OLTP source (4 tables)."""
import psycopg2

TABLES = ["customers", "products", "transactions", "transaction_items"]


def get_pg_conn(cfg):
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
    )


def extract_table(conn, table_name):
    """Return (columns, rows) for a full-load read of the given table."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    return columns, rows


def extract_all(conn):
    """Return {table_name: (columns, rows)} for every source table."""
    return {table: extract_table(conn, table) for table in TABLES}
