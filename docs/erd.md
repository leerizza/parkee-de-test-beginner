# ERD — Parkee POS (Sistem Kasir Minimarket)

## 1. OLTP Source (PostgreSQL, `raw` operational schema)

Single tenant, 4 tabel. `store_id` di `transactions` masih kolom mentah (angka 1-3),
belum ada tabel `stores` di level Beginner ini.

```mermaid
erDiagram
    customers ||--o{ transactions : "places"
    transactions ||--o{ transaction_items : "contains"
    products ||--o{ transaction_items : "sold as"

    customers {
        int customer_id PK
        varchar name
        varchar phone
        varchar email
        varchar gender
        varchar city
        timestamp created_at
    }

    products {
        int product_id PK
        varchar product_name
        varchar category
        varchar brand
        numeric unit_price
        boolean is_active
        timestamp created_at
    }

    transactions {
        int transaction_id PK
        int customer_id FK
        int store_id "raw, no dimension yet"
        timestamp transaction_date
        numeric total_amount
        varchar payment_method
        varchar status
    }

    transaction_items {
        int item_id PK
        int transaction_id FK
        int product_id FK
        int quantity
        numeric unit_price
        numeric discount
        numeric subtotal
    }
```

## 2. Star Schema (dbt mart, ClickHouse `analytics_marts`)

`fact_sales` berada di grain **satu baris per transaction item**. Filter
`status = 'completed'` sudah diterapkan sejak `stg_transactions` (staging),
supaya semua mart di atasnya otomatis konsisten tanpa perlu re-apply rule ini.

```mermaid
erDiagram
    dim_customer ||--o{ fact_sales : "customer_id"
    dim_product ||--o{ fact_sales : "product_id"
    dim_date ||--o{ fact_sales : "date_id"

    dim_customer {
        int customer_id PK
        varchar customer_name
        varchar phone
        varchar email
        varchar gender
        varchar city
        timestamp created_at
    }

    dim_product {
        int product_id PK
        varchar product_name
        varchar category
        varchar brand
        numeric unit_price
        boolean is_active
        timestamp created_at
    }

    dim_date {
        int date_id PK "YYYYMMDD"
        date date
        int year
        int quarter
        int month
        varchar month_name
        int day_of_week
        varchar day_name
        boolean is_weekend
    }

    fact_sales {
        int item_id PK
        int transaction_id
        int customer_id FK
        int product_id FK
        int date_id FK
        int store_id
        timestamp transaction_date
        varchar payment_method
        int quantity
        numeric unit_price
        numeric discount
        numeric subtotal
    }
```

## 3. Catatan Desain

- **Kenapa filter `status = 'completed'` di staging, bukan di fact?**
  Supaya semua mart (dan analisis ad-hoc di atas staging) otomatis konsisten
  memakai definisi "transaksi valid" yang sama, tanpa risiko lupa re-apply
  filter di tiap model turunan.
- **Kenapa `dim_date` di-generate, bukan diambil dari source?** Tidak ada
  tabel kalender di OLTP; date spine dibangun dari rentang
  `min(transaction_date)` s.d. `max(transaction_date)` di `stg_transactions`.
- **`store_id`** sengaja tetap kolom mentah di `fact_sales` (bukan FK ke
  dimensi toko) karena level Beginner belum mewajibkan `dim_store` — itu
  scope Intermediate.
