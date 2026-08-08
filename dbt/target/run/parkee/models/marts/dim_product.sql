
  
    
    
    
        
         


        insert into `analytics_marts`.`dim_product__dbt_backup`
        ("product_id", "product_name", "category", "brand", "unit_price", "is_active", "created_at")with products as (
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
  