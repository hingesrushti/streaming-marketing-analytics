import json, random, uuid
from datetime import date, timedelta, datetime
import numpy as np, pandas as pd

random.seed(42); np.random.seed(42)
START = date(2024, 1, 1); DAYS = 540; N_USERS = 8000
OUT = "data"; import os; os.makedirs(OUT, exist_ok=True)

# Channel "personalities": (share of signups, CAC-ish cost weight, monthly churn hazard, engagement mult)
CHANNELS = {
    "paid_social_tiktok": dict(share=0.24, cost=1.0, churn=0.11, eng=0.8),
    "paid_search_google": dict(share=0.20, cost=1.6, churn=0.07, eng=1.0),
    "paid_video_youtube": dict(share=0.14, cost=1.3, churn=0.09, eng=0.9),
    "email":              dict(share=0.10, cost=0.3, churn=0.06, eng=1.1),
    "referral":           dict(share=0.14, cost=0.4, churn=0.04, eng=1.3),
    "organic":            dict(share=0.18, cost=0.1, churn=0.05, eng=1.2),
}
PLANS = {"basic": 6.99, "standard": 10.99, "premium": 15.99}
PLAN_W = [0.45, 0.38, 0.17]
COUNTRIES = ["US", "GB", "CA", "DE", "BR", "IN"]

# ---- plans ----
pd.DataFrame([{"plan_tier": k, "monthly_price": v} for k, v in PLANS.items()]).to_csv(
    f"{OUT}/plans.csv", index=False)

# ---- users ----
ch_names = list(CHANNELS); ch_share = np.array([CHANNELS[c]["share"] for c in ch_names])
ch_share = ch_share / ch_share.sum()
users = []
for i in range(N_USERS):
    ch = np.random.choice(ch_names, p=ch_share)
    signup = date(2024, 1, 1) + timedelta(days=int(np.random.randint(0, DAYS - 60)))
    plan = np.random.choice(list(PLANS), p=PLAN_W)
    users.append(dict(user_id=f"u_{i:06d}", signup_date=signup.isoformat(),
                      acquisition_channel=ch, plan_tier=plan,
                      country=random.choice(COUNTRIES)))
users_df = pd.DataFrame(users); users_df.to_csv(f"{OUT}/users.csv", index=False)

# ---- subscription events (trial -> convert -> maybe cancel/reactivate) ----
sub_events, eng_events = [], []
for u in users:
    ch = CHANNELS[u["acquisition_channel"]]
    t0 = datetime.fromisoformat(u["signup_date"])
    sub_events.append(dict(event_id=str(uuid.uuid4()), user_id=u["user_id"],
                           event_type="trial_start", event_ts=t0.isoformat(),
                           plan_tier=u["plan_tier"]))
    # trial conversion probability inversely related to churn hazard
    if np.random.rand() < (0.85 - ch["churn"]):
        conv = t0 + timedelta(days=7)
        sub_events.append(dict(event_id=str(uuid.uuid4()), user_id=u["user_id"],
                               event_type="trial_convert", event_ts=conv.isoformat(),
                               plan_tier=u["plan_tier"]))
        # survival: draw tenure in months from a geometric-ish churn hazard
        months = 0; cur = conv
        while months < 24 and np.random.rand() > ch["churn"]:
            months += 1; cur = conv + timedelta(days=30 * months)
            if cur.date() > date(2024, 1, 1) + timedelta(days=DAYS):
                break
        if months < 24 and cur.date() <= date(2024, 1, 1) + timedelta(days=DAYS):
            sub_events.append(dict(event_id=str(uuid.uuid4()), user_id=u["user_id"],
                                   event_type="cancel", event_ts=cur.isoformat(),
                                   plan_tier=u["plan_tier"]))
            if np.random.rand() < 0.15:  # some win-backs
                re = cur + timedelta(days=random.randint(20, 120))
                if re.date() <= date(2024, 1, 1) + timedelta(days=DAYS):
                    sub_events.append(dict(event_id=str(uuid.uuid4()), user_id=u["user_id"],
                                           event_type="reactivate", event_ts=re.isoformat(),
                                           plan_tier=u["plan_tier"]))
        # engagement in first weeks (used to test the engagement->retention link)
        n_plays = np.random.poisson(6 * ch["eng"])
        for _ in range(n_plays):
            ts = conv + timedelta(days=int(np.random.randint(0, 28)),
                                  minutes=int(np.random.randint(0, 1440)))
            eng_events.append(dict(event_id=str(uuid.uuid4()), user_id=u["user_id"],
                                   event_ts=ts.isoformat(),
                                   content_id=f"c_{random.randint(1, 500):04d}",
                                   minutes_watched=int(np.clip(np.random.normal(38, 20), 1, 180))))

with open(f"{OUT}/subscription_events.json", "w") as f:
    for e in sub_events: f.write(json.dumps(e) + "\n")
with open(f"{OUT}/engagement_events.json", "w") as f:
    for e in eng_events: f.write(json.dumps(e) + "\n")

# ---- marketing spend (daily, tied loosely to signup volume per channel) ----
signups_by_day_ch = (users_df.assign(d=users_df.signup_date)
                     .groupby(["d", "acquisition_channel"]).size().reset_index(name="n"))
rows = []
for _, r in signups_by_day_ch.iterrows():
    ch = CHANNELS.get(r["acquisition_channel"])
    if ch is None or r["acquisition_channel"] == "organic":  # organic ~ no paid spend
        continue
    base_cpa = 12 * ch["cost"] * np.random.uniform(0.8, 1.2)
    spend = round(r["n"] * base_cpa, 2)
    clicks = int(r["n"] * np.random.uniform(8, 25))
    rows.append(dict(date=r["d"], channel=r["acquisition_channel"],
                     campaign=f'{r["acquisition_channel"]}_evergreen',
                     spend=spend, impressions=clicks * np.random.randint(10, 40),
                     clicks=clicks))
pd.DataFrame(rows).to_csv(f"{OUT}/marketing_spend.csv", index=False)
print("Generated:", {f: len(x) for f, x in
      [("users", users), ("sub_events", sub_events), ("eng_events", eng_events), ("spend", rows)]})