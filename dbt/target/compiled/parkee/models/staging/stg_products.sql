with source as (
    select * from `raw`.`products`
)

select
    product_id,
    product_name,
    category,
    brand,
    unit_price,
    is_active,
    created_at
from source