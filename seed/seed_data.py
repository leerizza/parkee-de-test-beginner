"""Generate dummy data for the Parkee POS OLTP database (Postgres).

Populates customers, products, transactions, transaction_items with
realistic-ish random data. Monthly transaction volume is intentionally
uneven (weighted random per month) so Q2 trend charts show real movement.
"""
import os
import random
from datetime import datetime, timedelta

import psycopg2
from faker import Faker

fake = Faker("id_ID")
random.seed(42)
Faker.seed(42)

N_CUSTOMERS = 180
N_PRODUCTS_PER_CATEGORY = (8, 12)
N_MONTHS = 9  # spread transactions across the last 9 months
N_TRANSACTIONS = 2500
PAYMENT_METHODS = ["cash", "debit", "credit", "e-wallet"]
PAYMENT_WEIGHTS = [0.35, 0.25, 0.15, 0.25]
STORE_IDS = [1, 2, 3]

CATEGORIES = {
    "Minuman": ["Coca-Cola", "Teh Botol", "Aqua", "Pocari Sweat", "Fanta"],
    "Snack": ["Chitato", "Taro", "Oreo", "Better", "Chiki Balls"],
    "Bahan Pokok": ["Beras", "Minyak Goreng", "Gula Pasir", "Tepung Terigu"],
    "Perawatan Diri": ["Sabun Lifebuoy", "Shampoo Sunsilk", "Pasta Gigi Pepsodent"],
    "Rumah Tangga": ["Sunlight", "Rinso", "Molto", "Kapas"],
    "Rokok": ["Sampoerna Mild", "Gudang Garam", "Marlboro"],
    "Bayi": ["Pampers", "SGM", "Bebelac"],
    "Kesehatan": ["Panadol", "Tolak Angin", "Betadine"],
}
BRANDS = ["Unilever", "Indofood", "Wings", "Nestle", "Danone", "P&G", "Local Brand"]


def get_conn():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ.get("POSTGRES_DB", "parkee_oltp"),
        user=os.environ.get("POSTGRES_USER", "parkee"),
        password=os.environ.get("POSTGRES_PASSWORD", "parkee"),
    )


def seed_customers(cur):
    rows = []
    for _ in range(N_CUSTOMERS):
        gender = random.choice(["male", "female"])
        name = fake.name_male() if gender == "male" else fake.name_female()
        created_at = fake.date_time_between(start_date="-2y", end_date="-9M")
        rows.append((
            name,
            fake.phone_number()[:20],
            fake.unique.email(),
            gender,
            fake.city(),
            created_at,
        ))
    cur.executemany(
        """INSERT INTO customers (name, phone, email, gender, city, created_at)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        rows,
    )


def seed_products(cur):
    rows = []
    for category, names in CATEGORIES.items():
        n = random.randint(*N_PRODUCTS_PER_CATEGORY)
        for i in range(n):
            base_name = random.choice(names)
            product_name = f"{base_name} {fake.word().capitalize()} {random.randint(1,999)}ml/gr"
            unit_price = round(random.uniform(2000, 150000), -2)
            is_active = random.random() > 0.05
            created_at = fake.date_time_between(start_date="-2y", end_date="-9M")
            rows.append((
                product_name,
                category,
                random.choice(BRANDS),
                unit_price,
                is_active,
                created_at,
            ))
    cur.executemany(
        """INSERT INTO products (product_name, category, brand, unit_price, is_active, created_at)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        rows,
    )


def month_weights(n_months):
    # Uneven weights to simulate seasonality (e.g. lower mid-year, spike near recent months)
    base = [0.6, 0.8, 1.0, 0.7, 0.9, 1.3, 1.5, 1.1, 1.8]
    weights = (base * ((n_months // len(base)) + 1))[:n_months]
    return weights


def seed_transactions_and_items(cur, n_customers, n_products, product_prices):
    today = datetime.now()
    months = []
    for i in range(N_MONTHS - 1, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=1)) if i == 0 else today
        months.append(i)

    weights = month_weights(N_MONTHS)
    month_offsets = list(range(N_MONTHS - 1, -1, -1))  # e.g. 8 months ago ... 0 (this month)

    txn_rows = []
    txn_month_choice = random.choices(month_offsets, weights=weights, k=N_TRANSACTIONS)

    transactions_data = []
    for months_ago in txn_month_choice:
        target_month = today.month - months_ago
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        max_day = min(28, today.day) if months_ago == 0 else 28
        day = random.randint(1, max_day)
        hour = random.randint(8, 21)
        minute = random.randint(0, 59)
        txn_date = datetime(target_year, target_month, day, hour, minute)
        status = random.choices(["completed", "cancelled", "pending"], weights=[0.92, 0.05, 0.03])[0]
        payment_method = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]
        customer_id = random.randint(1, n_customers)
        store_id = random.choice(STORE_IDS)
        transactions_data.append({
            "customer_id": customer_id,
            "store_id": store_id,
            "transaction_date": txn_date,
            "payment_method": payment_method,
            "status": status,
        })

    # Insert transactions with placeholder total_amount, then update after items are computed
    insert_txn_sql = """
        INSERT INTO transactions (customer_id, store_id, transaction_date, total_amount, payment_method, status)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING transaction_id
    """
    item_rows = []
    for t in transactions_data:
        n_items = random.randint(1, 6)
        chosen_products = random.sample(range(1, n_products + 1), min(n_items, n_products))
        items_for_txn = []
        total = 0
        for product_id in chosen_products:
            unit_price = product_prices[product_id - 1]
            quantity = random.randint(1, 5)
            discount = random.choice([0, 0, 0, 5, 10])
            subtotal = round(unit_price * quantity * (1 - discount / 100), 2)
            total += subtotal
            items_for_txn.append((product_id, quantity, unit_price, discount, subtotal))

        cur.execute(insert_txn_sql, (
            t["customer_id"], t["store_id"], t["transaction_date"],
            total, t["payment_method"], t["status"],
        ))
        transaction_id = cur.fetchone()[0]
        for product_id, quantity, unit_price, discount, subtotal in items_for_txn:
            item_rows.append((transaction_id, product_id, quantity, unit_price, discount, subtotal))

    cur.executemany(
        """INSERT INTO transaction_items (transaction_id, product_id, quantity, unit_price, discount, subtotal)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        item_rows,
    )
    return len(transactions_data), len(item_rows)


def main():
    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor()
    try:
        print("Seeding customers...")
        seed_customers(cur)

        print("Seeding products...")
        seed_products(cur)
        conn.commit()

        cur.execute("SELECT product_id, unit_price FROM products ORDER BY product_id")
        rows = cur.fetchall()
        product_prices = [float(r[1]) for r in rows]
        n_products = len(rows)

        cur.execute("SELECT count(*) FROM customers")
        n_customers = cur.fetchone()[0]

        print("Seeding transactions + transaction_items...")
        n_txn, n_items = seed_transactions_and_items(cur, n_customers, n_products, product_prices)
        conn.commit()

        cur.execute("SELECT count(*) FROM customers")
        c_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM products")
        p_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM transactions")
        t_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM transaction_items")
        i_count = cur.fetchone()[0]

        print("Seed complete:")
        print(f"  customers:         {c_count}")
        print(f"  products:          {p_count}")
        print(f"  transactions:      {t_count}")
        print(f"  transaction_items: {i_count}")

        cur.execute("""
            SELECT date_trunc('month', transaction_date)::date AS month, count(*)
            FROM transactions
            GROUP BY 1 ORDER BY 1
        """)
        print("\nMonthly transaction distribution:")
        for month, cnt in cur.fetchall():
            print(f"  {month}: {cnt}")

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
