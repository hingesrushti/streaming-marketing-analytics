select
    user_id,
    cast(signup_date as date) as signup_date,
    lower(acquisition_channel) as acquisition_channel,
    lower(plan_tier) as plan_tier,
    upper(country) as country
from {{ source('bronze', 'users') }}
