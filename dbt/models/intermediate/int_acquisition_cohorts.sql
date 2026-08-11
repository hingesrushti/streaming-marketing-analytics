select
    date_trunc('month', signup_date) as cohort_month,
    acquisition_channel,
    count(distinct user_id) as cohort_size
from {{ ref('stg_users') }}
group by 
    date_trunc('month', signup_date),
    acquisition_channel
