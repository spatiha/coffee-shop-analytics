"""
Synthetic data generator for a 3-store specialty coffee chain.

Generates 18 months of transactions (Jan 2025 - Jun 2026) with realistic
structure baked in, so the SQL layer has real patterns to find:

- daypart peaks (7-9am commuter rush, 12-1pm lunch, weekend mid-morning)
- seasonality (hot drinks in winter, cold brew in summer)
- customer segments with different visit habits (commuters, students,
  weekenders, occasionals)
- product affinities (croissants ride along with lattes)
- a loyalty program launched Aug 2025 that lifts member frequency
- a ~4% price increase on espresso drinks in Jan 2026

Output: data/stores.csv, data/products.csv, data/customers.csv,
        data/transactions.csv, data/order_items.csv
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

RNG = np.random.default_rng(2026)

START, END = date(2025, 1, 1), date(2026, 6, 30)

# ---------------------------------------------------------------- stores
stores = pd.DataFrame([
    (1, "Downtown", "financial district", 340),
    (2, "University", "campus edge", 260),
    (3, "Parkside", "residential", 180),
], columns=["store_id", "store_name", "location_type", "base_daily_orders"])

# ---------------------------------------------------------------- products
products = pd.DataFrame([
    # product_id, name, category, price, cost, temp
    (1, "Espresso", "espresso", 3.25, 0.55, "hot"),
    (2, "Americano", "espresso", 3.75, 0.60, "hot"),
    (3, "Latte", "espresso", 5.25, 1.10, "hot"),
    (4, "Cappuccino", "espresso", 5.00, 1.05, "hot"),
    (5, "Flat White", "espresso", 5.25, 1.10, "hot"),
    (6, "Mocha", "espresso", 5.75, 1.35, "hot"),
    (7, "Caramel Latte", "espresso", 5.95, 1.40, "hot"),
    (8, "Drip Coffee", "brewed", 2.95, 0.40, "hot"),
    (9, "Pour Over", "brewed", 4.50, 0.85, "hot"),
    (10, "Cold Brew", "cold", 4.95, 0.90, "cold"),
    (11, "Iced Latte", "cold", 5.50, 1.15, "cold"),
    (12, "Nitro Cold Brew", "cold", 5.75, 1.05, "cold"),
    (13, "Iced Matcha Latte", "cold", 5.95, 1.45, "cold"),
    (14, "Chai Latte", "tea", 4.95, 1.00, "hot"),
    (15, "Earl Grey", "tea", 3.25, 0.45, "hot"),
    (16, "Green Tea", "tea", 3.25, 0.45, "hot"),
    (17, "Hot Chocolate", "other_drink", 4.50, 1.10, "hot"),
    (18, "Butter Croissant", "bakery", 3.95, 1.20, None),
    (19, "Almond Croissant", "bakery", 4.75, 1.55, None),
    (20, "Blueberry Muffin", "bakery", 3.75, 1.10, None),
    (21, "Banana Bread", "bakery", 3.95, 1.05, None),
    (22, "Chocolate Chip Cookie", "bakery", 2.95, 0.80, None),
    (23, "Ham & Cheese Croissant", "food", 6.50, 2.40, None),
    (24, "Avocado Toast", "food", 8.95, 3.10, None),
    (25, "Breakfast Sandwich", "food", 7.95, 2.90, None),
    (26, "Granola Bowl", "food", 7.50, 2.60, None),
    (27, "12oz Whole Bean Bag", "retail", 16.95, 8.20, None),
    (28, "Ceramic Mug", "retail", 14.95, 6.00, None),
], columns=["product_id", "product_name", "category", "price", "cost", "temp"])

# ---------------------------------------------------------------- customers
N_CUST = 9000
seg = RNG.choice(["commuter", "student", "weekender", "occasional"],
                 N_CUST, p=[0.18, 0.22, 0.20, 0.40])
home = np.where(seg == "commuter", 1,
        np.where(seg == "student", 2,
         RNG.choice([1, 2, 3], N_CUST, p=[0.25, 0.25, 0.50])))
join_offsets = RNG.integers(0, (END - START).days - 30, N_CUST)
customers = pd.DataFrame({
    "customer_id": np.arange(1, N_CUST + 1),
    "segment": seg,
    "home_store_id": home,
    "signup_date": [START + timedelta(days=int(o)) for o in join_offsets],
})
# Loyalty program launches 2025-08-01; adoption skews to frequent segments
loyal_p = customers.segment.map(
    {"commuter": 0.65, "student": 0.50, "weekender": 0.35, "occasional": 0.12})
is_member = RNG.random(N_CUST) < loyal_p
member_offsets = RNG.integers(0, 200, N_CUST)
customers["loyalty_join_date"] = [
    max(date(2025, 8, 1) + timedelta(days=int(o)), sd) if m else None
    for m, o, sd in zip(is_member, member_offsets, customers.signup_date)]

# ------------------------------------------------- visit probability model
VISIT_P = {"commuter": 0.42, "student": 0.30, "weekender": 0.18, "occasional": 0.05}
WEEKEND_MULT = {"commuter": 0.25, "student": 0.7, "weekender": 3.2, "occasional": 1.4}

def daypart_hour(segment, is_weekend):
    if is_weekend:
        return int(np.clip(RNG.normal(10.5, 2.2), 7, 19))
    r = RNG.random()
    if segment == "commuter":
        return int(np.clip(RNG.normal(8.0, 1.0), 6, 19)) if r < 0.75 else \
               int(np.clip(RNG.normal(12.5, 1.2), 6, 19))
    if segment == "student":
        return int(np.clip(RNG.normal(14.0, 3.0), 7, 20))
    return int(np.clip(RNG.normal(11.0, 3.0), 6, 19))

def pick_drink(month, price_bump):
    drinks = products[products.category.isin(
        ["espresso", "brewed", "cold", "tea", "other_drink"])]
    cold = drinks[drinks.temp == "cold"]
    hot = drinks[drinks.temp == "hot"]
    cold_share = 0.14 + (0.28 if month in (6, 7, 8) else
                         0.20 if month in (5, 9) else 0.0)
    pool = cold if RNG.random() < cold_share else hot
    w = np.where(pool.category == "espresso", 3.0,
         np.where(pool.category == "brewed", 1.6,
          np.where(pool.category == "cold", 1.5, 0.8)))
    row = pool.sample(1, weights=w, random_state=int(RNG.integers(1e9))).iloc[0]
    price = row.price
    if row.category == "espresso" and price_bump:
        price = round(price * 1.04, 2)
    return row.product_id, price

FOOD_AFFINITY = {  # P(attach) given drink category
    "espresso": 0.38, "brewed": 0.30, "cold": 0.22, "tea": 0.25, "other_drink": 0.30}

def maybe_food(drink_pid, hour):
    cat = products.set_index("product_id").loc[drink_pid, "category"]
    if RNG.random() > FOOD_AFFINITY.get(cat, 0.2):
        return None
    # croissants ride with lattes; sandwiches at breakfast/lunch
    if drink_pid in (3, 4, 5, 7) and RNG.random() < 0.45:
        return int(RNG.choice([18, 19], p=[0.65, 0.35]))
    if 6 <= hour <= 10 and RNG.random() < 0.4:
        return int(RNG.choice([25, 23, 20], p=[0.45, 0.3, 0.25]))
    if 11 <= hour <= 14 and RNG.random() < 0.35:
        return int(RNG.choice([24, 23, 26], p=[0.4, 0.35, 0.25]))
    return int(RNG.choice([20, 21, 22, 18], p=[0.3, 0.25, 0.25, 0.2]))



PRODUCTS_IDX = products.set_index("product_id")
HOT_POOL = products[(products.temp == "hot")]
COLD_POOL = products[(products.temp == "cold")]

def _pool_weights(pool):
    return np.where(pool.category == "espresso", 3.0,
            np.where(pool.category == "brewed", 1.6,
             np.where(pool.category == "cold", 1.5, 0.8))).astype(float)

HOT_W = _pool_weights(HOT_POOL); HOT_W /= HOT_W.sum()
COLD_W = _pool_weights(COLD_POOL); COLD_W /= COLD_W.sum()


def main():
    cust = customers.copy()
    cust["signup_date"] = pd.to_datetime(cust.signup_date).dt.date
    cust["loyalty_join_date"] = pd.to_datetime(cust.loyalty_join_date).dt.date
    seg_arr = cust.segment.to_numpy()
    base_visit = cust.segment.map(VISIT_P).to_numpy()
    wknd_mult = cust.segment.map(WEEKEND_MULT).to_numpy()
    signup = cust.signup_date.to_numpy()
    loyal_date = cust.loyalty_join_date.to_numpy()
    home_arr = cust.home_store_id.to_numpy()
    cid_arr = cust.customer_id.to_numpy()

    tx_parts, item_parts = [], []
    tx_id_start = 1
    day = START
    while day <= END:
        is_weekend = day.weekday() >= 5
        month = day.month
        price_bump = day >= date(2026, 1, 6)

        active = signup <= day
        p = base_visit.copy()
        if is_weekend:
            p = p * wknd_mult
        member_now = np.array([(d is not None and not pd.isna(d) and d <= day)
                               for d in loyal_date])
        p = p * np.where(member_now, 1.20, 1.0)
        p = p * (1 + 0.00035 * (day - START).days)
        p = np.where(active, np.clip(p, 0, 0.95), 0.0)

        visit = RNG.random(len(p)) < p
        n = int(visit.sum())
        if n == 0:
            day += timedelta(days=1); continue

        v_seg = seg_arr[visit]; v_cid = cid_arr[visit]
        v_home = home_arr[visit]; v_member = member_now[visit]

        # hours, vectorized by segment
        hours = np.empty(n)
        if is_weekend:
            hours = RNG.normal(10.5, 2.2, n)
        else:
            hours = RNG.normal(11.0, 3.0, n)
            com = v_seg == "commuter"
            n_com = int(com.sum())
            split = RNG.random(n_com) < 0.75
            h_com = np.where(split, RNG.normal(8.0, 1.0, n_com),
                             RNG.normal(12.5, 1.2, n_com))
            hours[com] = h_com
            stu = v_seg == "student"
            hours[stu] = RNG.normal(14.0, 3.0, int(stu.sum()))
        hours = np.clip(hours, 6, 19).astype(int)
        minutes = RNG.integers(0, 60, n)

        stay_home = RNG.random(n) < 0.8
        store = np.where(stay_home, v_home,
                         RNG.choice(stores.store_id.to_numpy(), n))

        # drinks
        cold_share = 0.14 + (0.28 if month in (6, 7, 8) else
                             0.20 if month in (5, 9) else 0.0)
        go_cold = RNG.random(n) < cold_share
        drink_pid = np.where(
            go_cold,
            RNG.choice(COLD_POOL.product_id.to_numpy(), n, p=COLD_W),
            RNG.choice(HOT_POOL.product_id.to_numpy(), n, p=HOT_W))
        drink_price = PRODUCTS_IDX.loc[drink_pid, "price"].to_numpy()
        drink_cat = PRODUCTS_IDX.loc[drink_pid, "category"].to_numpy()
        if price_bump:
            drink_price = np.where(drink_cat == "espresso",
                                   np.round(drink_price * 1.04, 2), drink_price)
        qty = np.where(RNG.random(n) < 0.07, 2, 1)

        # food attach
        aff = pd.Series(drink_cat).map(FOOD_AFFINITY).fillna(0.2).to_numpy()
        attach = RNG.random(n) < aff
        latte_like = np.isin(drink_pid, [3, 4, 5, 7])
        r1 = RNG.random(n); r2 = RNG.random(n)
        food_pid = np.full(n, -1)
        # default pastry pick
        food_pid[attach] = RNG.choice([20, 21, 22, 18], int(attach.sum()),
                                      p=[0.3, 0.25, 0.25, 0.2])
        m = attach & (11 <= hours) & (hours <= 14) & (r2 < 0.35)
        food_pid[m] = RNG.choice([24, 23, 26], int(m.sum()), p=[0.4, 0.35, 0.25])
        m = attach & (6 <= hours) & (hours <= 10) & (r2 < 0.4)
        food_pid[m] = RNG.choice([25, 23, 20], int(m.sum()), p=[0.45, 0.3, 0.25])
        m = attach & latte_like & (r1 < 0.45)
        food_pid[m] = RNG.choice([18, 19], int(m.sum()), p=[0.65, 0.35])

        retail = RNG.random(n) < 0.015
        retail_pid = np.where(RNG.random(n) < 0.7, 27, 28)

        tx_ids = np.arange(tx_id_start, tx_id_start + n)
        tx_id_start += n
        ts = [f"{day} {h:02d}:{m:02d}:00" for h, m in zip(hours, minutes)]
        tx_parts.append(pd.DataFrame({
            "transaction_id": tx_ids, "customer_id": v_cid,
            "store_id": store, "transaction_ts": ts,
            "is_loyalty_member": v_member}))

        items = [pd.DataFrame({"transaction_id": tx_ids,
                               "product_id": drink_pid,
                               "quantity": qty, "unit_price": drink_price})]
        if attach.any():
            fp = food_pid[attach]
            items.append(pd.DataFrame({
                "transaction_id": tx_ids[attach], "product_id": fp,
                "quantity": 1,
                "unit_price": PRODUCTS_IDX.loc[fp, "price"].to_numpy()}))
        if retail.any():
            rp = retail_pid[retail]
            items.append(pd.DataFrame({
                "transaction_id": tx_ids[retail], "product_id": rp,
                "quantity": 1,
                "unit_price": PRODUCTS_IDX.loc[rp, "price"].to_numpy()}))
        item_parts.append(pd.concat(items))
        day += timedelta(days=1)

    tx = pd.concat(tx_parts, ignore_index=True)
    it = pd.concat(item_parts, ignore_index=True).sort_values(
        ["transaction_id"]).reset_index(drop=True)
    it.insert(0, "order_item_id", np.arange(1, len(it) + 1))
    tx.to_csv("data/transactions.csv", index=False)
    it.to_csv("data/order_items.csv", index=False)
    stores.to_csv("data/stores.csv", index=False)
    products.drop(columns="temp").to_csv("data/products.csv", index=False)
    customers.to_csv("data/customers.csv", index=False)
    print(f"transactions: {len(tx):,}  |  line items: {len(it):,}")


if __name__ == "__main__":
    main()
