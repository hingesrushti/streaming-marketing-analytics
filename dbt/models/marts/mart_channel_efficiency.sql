with ltv as (
    select
        acquisition_channel,
        count(distinct user_id) as subscribers,
        avg(tenure_months * monthly_price) as avg_ltv,
        avg(monthly_price) as avg_monthly_price
    from {{ ref('int_subscription_spells') }}
    group by acquisition_channel
),

cac as (
    select
        acquisition_channel,
        cac,
        total_spend,
        new_subscribers
    from {{ ref('mart_channel_cac') }}
)

select
    l.acquisition_channel,
    l.subscribers,
    round(l.avg_ltv, 2) as ltv,
    round(coalesce(c.cac, 0), 2) as cac,
    round(
        l.avg_ltv / nullif(c.cac, 0),
        2
    ) as ltv_to_cac_ratio,
    round(
        c.cac / nullif(l.avg_monthly_price, 0),
        1
    ) as payback_months,
    c.total_spend,
    c.new_subscribers
from ltv l
left join cac c using (acquisition_channel)
order by ltv_to_cac_ratio desc nulls last
