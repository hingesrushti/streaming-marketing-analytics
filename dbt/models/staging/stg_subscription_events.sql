select
    event_id,
    user_id,
    lower(event_type) as event_type,
    cast(event_ts as timestamp) as event_ts,
    lower(plan_tier) as plan_tier
from {{ source('bronze', 'subscription_events') }}
