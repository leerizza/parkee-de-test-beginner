
    
    

with child as (
    select date_id as from_field
    from `analytics_marts`.`fact_sales`
    where date_id is not null
),

parent as (
    select date_id as to_field
    from `analytics_marts`.`dim_date`
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null
-- end_of_sql
settings join_use_nulls = 1


