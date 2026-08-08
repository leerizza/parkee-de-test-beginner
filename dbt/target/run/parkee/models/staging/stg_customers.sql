

  create or replace view `analytics_staging`.`stg_customers` 
  
    
  
  
    
    
  as (
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
    
  )
      
      
                    -- end_of_sql
                    
                    