
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select status
from `analytics_staging`.`stg_transactions`
where status is null



  
  
    ) dbt_internal_test