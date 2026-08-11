with user_signups as (
    select 
        user_id,
        signup_date
    from {{ ref('stg_users') }}
),

early_engagement as (
    select
        e.user_id,
        sum(e.minutes_watched) as total_minutes_first_28_days,
        count(distinct e.event_id) as play_count_first_28_days
    from {{ ref('stg_engagement_events') }} e
    join user_signups u on e.user_id = u.user_id
    where date(e.event_ts) between u.signup_date and date_add(u.signup_date, 28)
    group by e.user_id
)

select * from early_engagement
