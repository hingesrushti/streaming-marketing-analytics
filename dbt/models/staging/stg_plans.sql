select
    lower(plan_tier) as plan_tier,
    monthly_price
from {{ source('bronze', 'plans') }}
