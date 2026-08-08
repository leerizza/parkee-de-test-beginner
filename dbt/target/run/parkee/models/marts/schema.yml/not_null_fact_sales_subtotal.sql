
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select subtotal
from `analytics_marts`.`fact_sales`
where subtotal is null



  
  
    ) dbt_internal_test