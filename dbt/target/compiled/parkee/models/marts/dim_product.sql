with products as (
    select * from `analytics_staging`.`stg_products`
)

select
    product_id,
    product_name,
    category,
    brand,
    unit_price,
    is_active,
    created_at
from products