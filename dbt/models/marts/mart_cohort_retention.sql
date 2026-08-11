with cohort_base as (
    select
        date_trunc('month', signup_date) as cohort_month,
        acquisition_channel,
        count(distinct user_id) as cohort_size
    from {{ ref('stg_users') }}
    group by date_trunc('month', signup_date), acquisition_channel
),

cohort_activity as (
    select
        date_trunc('month', u.signup_date) as cohort_month,
        u.acquisition_channel,
        s.is_active,
        count(distinct s.user_id) as active_count
    from {{ ref('int_subscription_spells') }} s
    join {{ ref('stg_users') }} u on s.user_id = u.user_id
    group by 
        date_trunc('month', u.signup_date),
        u.acquisition_channel,
        s.is_active
)

select
    b.cohort_month,
    b.acquisition_channel,
    b.cohort_size,
    coalesce(a.active_count, 0) as still_active,
    round(
        coalesce(a.active_count, 0) * 100.0 / nullif(b.cohort_size, 0),
        1
    ) as retention_pct
from cohort_base b
left join cohort_activity a
    on b.cohort_month = a.cohort_month
    and b.acquisition_channel = a.acquisition_channel
    and a.is_active = true
order by b.cohort_month desc, b.acquisition_channel
