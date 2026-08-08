with customers as (
    select * from `analytics_staging`.`stg_customers`
)

select
    customer_id,
    customer_name,
    phone,
    email,
    gender,
    city,
    created_at
from customers