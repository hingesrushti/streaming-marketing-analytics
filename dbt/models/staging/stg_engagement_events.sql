select
    event_id,
    user_id,
    cast(event_ts as timestamp) as event_ts,
    content_id,
    minutes_watched
from {{ source('bronze', 'engagement_events') }}
