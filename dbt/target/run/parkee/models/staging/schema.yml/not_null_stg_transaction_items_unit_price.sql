
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select unit_price
from `analytics_staging`.`stg_transaction_items`
where unit_price is null



  
  
    ) dbt_internal_test