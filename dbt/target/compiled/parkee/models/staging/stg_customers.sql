with source as (
    select * from `raw`.`customers`
)

select
    customer_id,
    name as customer_name,
    phone,
    email,
    gender,
    city,
    created_at
from source