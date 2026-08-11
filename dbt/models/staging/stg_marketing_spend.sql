select
    cast(date as date) as date,
    lower(channel) as channel,
    lower(campaign) as campaign,
    spend,
    impressions,
    clicks
from {{ source('bronze', 'marketing_spend') }}
