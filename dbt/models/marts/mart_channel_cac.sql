with spend_by_channel as (
    select
        channel as acquisition_channel,
        sum(spend) as total_spend,
        sum(clicks) as total_clicks
    from {{ ref('stg_marketing_spend') }}
    group by channel
),

signups_by_channel as (
    select
        acquisition_channel,
        count(distinct user_id) as new_subscribers
    from {{ ref('stg_users') }}
    group by acquisition_channel
)

select
    s.acquisition_channel,
    coalesce(sp.total_spend, 0) as total_spend,
    s.new_subscribers,
    round(
        coalesce(sp.total_spend, 0) / nullif(s.new_subscribers, 0),
        2
    ) as cac
from signups_by_channel s
left join spend_by_channel sp
    on s.acquisition_channel = sp.acquisition_channel
order by cac desc
