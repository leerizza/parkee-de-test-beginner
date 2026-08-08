
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select subtotal
from `analytics_staging`.`stg_transaction_items`
where subtotal is null



  
  
    ) dbt_internal_test