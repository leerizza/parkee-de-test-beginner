with transactions as (
    select * from {{ ref('stg_transactions') }}
),

transaction_items as (
    select * from {{ ref('stg_transaction_items') }}
)

select
    ti.item_id,
    t.transaction_id as transaction_id,
    t.customer_id,
    ti.product_id,
    toYYYYMMDD(t.transaction_date::date) as date_id,
    t.store_id,
    t.transaction_date,
    t.payment_method,
    ti.quantity,
    ti.unit_price,
    ti.discount,
    ti.subtotal
from transaction_items as ti
inner join transactions as t
    on ti.transaction_id = t.transaction_id
