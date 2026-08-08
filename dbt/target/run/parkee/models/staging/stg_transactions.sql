

  create or replace view `analytics_staging`.`stg_transactions` 
  
    
  
  
    
    
  as (
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
    
  )
      
      
                    -- end_of_sql
                    
                    