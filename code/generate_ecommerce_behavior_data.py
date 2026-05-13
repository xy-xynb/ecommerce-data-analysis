import numpy as np
import pandas as pd
from pathlib import Path

SEED = 20260512
TARGET_ROWS = 50_000
rng = np.random.default_rng(SEED)

n_users = 5_000
n_items = 3_000
n_categories = 80

user_ids = np.arange(1, n_users + 1)
item_ids = np.arange(1, n_items + 1)
category_ids = np.arange(1, n_categories + 1)

item_category = rng.choice(category_ids, size=n_items, replace=True)
item_category_map = dict(zip(item_ids, item_category))

category_price_center = {
    cid: float(np.round(rng.lognormal(mean=3.2, sigma=0.7), 2))
    for cid in category_ids
}

user_segment = rng.choice(
    ["low_value", "mid_value", "high_value"],
    size=n_users,
    p=[0.60, 0.30, 0.10]
)

activity_weight_map = {"low_value": 1.0, "mid_value": 2.3, "high_value": 5.0}
buy_propensity_map = {"low_value": 0.035, "mid_value": 0.070, "high_value": 0.130}
price_preference_map = {"low_value": 0.85, "mid_value": 1.00, "high_value": 1.25}

user_activity_weight = np.array([activity_weight_map[s] for s in user_segment])
user_buy_propensity = np.array([buy_propensity_map[s] for s in user_segment])
user_price_preference = np.array([price_preference_map[s] for s in user_segment])
user_pick_prob = user_activity_weight / user_activity_weight.sum()

item_popularity = rng.zipf(a=1.6, size=n_items).astype(float)
item_popularity = item_popularity / item_popularity.sum()

start_time = pd.Timestamp("2026-01-01 00:00:00")
end_time = pd.Timestamp("2026-03-31 23:59:59")

hour_weights = np.array([
    0.20, 0.15, 0.10, 0.08, 0.08, 0.12,
    0.30, 0.55, 0.80, 1.00, 1.20, 1.35,
    1.25, 1.10, 1.05, 1.10, 1.25, 1.55,
    1.85, 2.05, 2.10, 1.70, 1.00, 0.45
], dtype=float)
hour_prob = hour_weights / hour_weights.sum()

weekday_weights = np.array([0.92, 0.95, 1.00, 1.02, 1.08, 1.28, 1.22])
weekday_prob = weekday_weights / weekday_weights.sum()

def random_base_time():
    target_weekday = rng.choice(np.arange(7), p=weekday_prob)
    possible_dates = pd.date_range(start_time.normalize(), end_time.normalize(), freq="D")
    possible_dates = possible_dates[possible_dates.weekday == target_weekday]
    day = rng.choice(possible_dates)
    hour = int(rng.choice(np.arange(24), p=hour_prob))
    minute = int(rng.integers(0, 60))
    second = int(rng.integers(0, 60))
    return pd.Timestamp(day) + pd.Timedelta(hours=hour, minutes=minute, seconds=second)

def generate_price(category_id, user_idx):
    center = category_price_center[category_id]
    user_factor = user_price_preference[user_idx]
    noise = rng.lognormal(mean=0, sigma=0.25)
    price = center * user_factor * noise
    return float(np.round(np.clip(price, 5, 9999), 2))

rows = []

while len(rows) < TARGET_ROWS:
    user_idx = rng.choice(np.arange(n_users), p=user_pick_prob)
    user_id = int(user_ids[user_idx])
    item_id = int(rng.choice(item_ids, p=item_popularity))
    category_id = int(item_category_map[item_id])
    price = generate_price(category_id, user_idx)

    t0 = random_base_time()
    rows.append([user_id, item_id, category_id, "pv", t0, price])

    buy_p = user_buy_propensity[user_idx]
    cart_p = min(0.24, buy_p * 2.2 + 0.04)
    fav_p = min(0.20, buy_p * 1.7 + 0.035)

    has_cart = rng.random() < cart_p
    has_fav = rng.random() < fav_p

    middle_events = []
    if has_cart:
        middle_events.append("cart")
    if has_fav:
        middle_events.append("fav")
    rng.shuffle(middle_events)

    current_time = t0
    for event in middle_events:
        current_time = current_time + pd.Timedelta(minutes=int(rng.integers(1, 180)))
        if current_time <= end_time:
            rows.append([user_id, item_id, category_id, event, current_time, price])

    final_buy_p = buy_p
    if has_cart:
        final_buy_p += 0.16
    if has_fav:
        final_buy_p += 0.07
    final_buy_p = min(final_buy_p, 0.55)

    if rng.random() < final_buy_p:
        current_time = current_time + pd.Timedelta(minutes=int(rng.integers(5, 1440)))
        if current_time <= end_time:
            rows.append([user_id, item_id, category_id, "buy", current_time, price])

df = pd.DataFrame(
    rows[:TARGET_ROWS],
    columns=["user_id", "item_id", "category_id", "behavior_type", "behavior_time", "price"]
)

df = df.sort_values("behavior_time").reset_index(drop=True)
df.to_csv("ecommerce_user_behavior_simulated_50000.csv", index=False, encoding="utf-8-sig")

print(df.head())
print(df["behavior_type"].value_counts())