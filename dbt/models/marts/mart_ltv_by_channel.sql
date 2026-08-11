select
    acquisition_channel,
    count(distinct user_id) as total_subscribers,
    count(distinct case when is_active then user_id end) as active_subscribers,
    round(avg(tenure_months * monthly_price), 2) as avg_ltv,
    round(avg(tenure_months), 1) as avg_tenure_months
from {{ ref('int_subscription_spells') }}
group by acquisition_channel
order by avg_ltv desc
