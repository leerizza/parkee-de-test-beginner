with source as (
    select * from `raw`.`transactions`
)

select
    transaction_id,
    customer_id,
    store_id,
    transaction_date,
    total_amount,
    payment_method,
    status
from source
where status = 'completed'