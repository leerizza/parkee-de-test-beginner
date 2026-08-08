with date_bounds as (
    select
        min(transaction_date)::date as min_date,
        max(transaction_date)::date as max_date
    from `analytics_staging`.`stg_transactions`
),

date_spine as (
    select
        (min_date + number)::date as date_day
    from date_bounds
    array join range(toUInt32(max_date - min_date) + 1) as number
)

select
    toYYYYMMDD(date_day) as date_id,
    date_day as date,
    toYear(date_day) as year,
    toQuarter(date_day) as quarter,
    toMonth(date_day) as month,
    dateName('month', date_day) as month_name,
    toDayOfMonth(date_day) as day_of_month,
    toDayOfWeek(date_day) as day_of_week,
    dateName('weekday', date_day) as day_name,
    toISOWeek(date_day) as iso_week,
    if(toDayOfWeek(date_day) in (6, 7), true, false) as is_weekend
from date_spine