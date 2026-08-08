

  create or replace view `analytics_staging`.`stg_transaction_items` 
  
    
  
  
    
    
  as (
    with source as (
    select * from `raw`.`transaction_items`
)

select
    item_id,
    transaction_id,
    product_id,
    quantity,
    unit_price,
    discount,
    subtotal
from source
    
  )
      
      
                    -- end_of_sql
                    
                    