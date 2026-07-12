"""
Loads the CSVs into DuckDB, runs every query in sql/, writes each result
to results/, and renders the three README figures.

Usage: python src/run_analysis.py
"""

import glob
import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

con = duckdb.connect()
for name in ["stores", "products", "customers", "transactions", "order_items"]:
    con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_csv_auto('data/{name}.csv')")

os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)

frames = {}
for path in sorted(glob.glob("sql/*.sql")):
    name = os.path.basename(path).replace(".sql", "")
    df = con.execute(open(path).read()).df()
    df.to_csv(f"results/{name}.csv", index=False)
    frames[name] = df
    print(f"{name}: {len(df)} rows")

# ---- Figure 1: monthly revenue trend
m = frames["01_monthly_revenue_trends"]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(pd.to_datetime(m["month"]), m["revenue"], marker="o", label="revenue")
ax.plot(pd.to_datetime(m["month"]), m["revenue_3mo_avg"], ls="--",
        label="3-month avg")
ax.set_title("Monthly revenue, all stores")
ax.set_ylabel("revenue ($)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/monthly_revenue.png", dpi=150)

# ---- Figure 2: cohort retention heatmap
c = frames["06_cohort_retention"]
pivot = c.pivot(index="cohort_month", columns="months_since_first",
                values="retention_pct")
pivot.index = pd.to_datetime(pivot.index).strftime("%Y-%m")
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(pivot.values, aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)
ax.set_xticks(range(pivot.shape[1]), pivot.columns)
ax.set_yticks(range(pivot.shape[0]), pivot.index)
ax.set_xlabel("months since first purchase")
ax.set_title("Cohort retention (%)")
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        v = pivot.values[i, j]
        if pd.notna(v):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6,
                    color="black" if v < 60 else "white")
fig.colorbar(im, shrink=0.8)
fig.tight_layout()
fig.savefig("figures/cohort_retention.png", dpi=150)

# ---- Figure 3: seasonality
s = frames["05_seasonality_hot_vs_cold"]
fig, ax = plt.subplots(figsize=(9, 4.5))
months = pd.to_datetime(s["month"])
ax.bar(months, s["hot_drink_revenue"], width=20, label="hot drinks")
ax.bar(months, s["cold_drink_revenue"], width=20,
       bottom=s["hot_drink_revenue"], label="cold drinks")
ax2 = ax.twinx()
ax2.plot(months, s["cold_share_pct"], color="black", marker="o", ms=4,
         label="cold share %")
ax2.set_ylabel("cold share (%)")
ax.set_title("Drink revenue mix by month")
ax.set_ylabel("revenue ($)")
ax.legend(loc="upper left")
fig.tight_layout()
fig.savefig("figures/seasonality.png", dpi=150)

print("figures saved")
