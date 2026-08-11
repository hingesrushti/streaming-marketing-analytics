with events as (
    select * from {{ ref('stg_subscription_events') }}
),

converts as (
    -- Find when each user converted from trial to paid
    select 
        user_id,
        min(event_ts) as converted_at
    from events 
    where event_type = 'trial_convert'
    group by user_id
),

cancels as (
    -- Find when each user canceled (if they did)
    select 
        user_id,
        min(event_ts) as canceled_at
    from events 
    where event_type = 'cancel'
    group by user_id
)

select
    u.user_id,
    u.acquisition_channel,
    u.plan_tier,
    date(c.converted_at) as converted_date,
    date(x.canceled_at) as canceled_date,
    (x.canceled_at is null) as is_active,
    -- Calculate tenure in months
    coalesce(
        datediff(month, c.converted_at, x.canceled_at),
        datediff(month, c.converted_at, current_date())
    ) as tenure_months,
    p.monthly_price
from {{ ref('stg_users') }} u
join converts c on u.user_id = c.user_id
left join cancels x on u.user_id = x.user_id
join {{ ref('stg_plans') }} p on u.plan_tier = p.plan_tier
