# Dashboard spec — Coffee Shop Analytics

Build target: Power BI (.pbix committed to this repo + screenshots in README),
with a Tableau Public rebuild of page 1 for a shareable interactive link.

## Data model

Load the five CSVs from `data/` as a star schema:

- Fact: `order_items` (grain: line item)
- Fact: `transactions` (grain: order) — related to order_items 1:many
- Dims: `products`, `stores`, `customers`, plus a DAX date table

Relationships: order_items → transactions (transaction_id),
order_items → products (product_id), transactions → stores (store_id),
transactions → customers (customer_id), transactions → Date (transaction_ts).

## Core DAX measures

```dax
Revenue = SUMX(order_items, order_items[quantity] * order_items[unit_price])

Orders = DISTINCTCOUNT(transactions[transaction_id])

AOV = DIVIDE([Revenue], [Orders])

Gross Profit =
SUMX(order_items,
     order_items[quantity] *
     (order_items[unit_price] - RELATED(products[cost])))

Margin % = DIVIDE([Gross Profit], [Revenue])

Revenue PY = CALCULATE([Revenue], SAMEPERIODLASTYEAR('Date'[Date]))

Revenue YoY % = DIVIDE([Revenue] - [Revenue PY], [Revenue PY])

Active Customers = DISTINCTCOUNT(transactions[customer_id])

Orders per Customer = DIVIDE([Orders], [Active Customers])

Loyalty Revenue % =
DIVIDE(
    CALCULATE([Revenue], transactions[is_loyalty_member] = TRUE()),
    [Revenue])
```

## Page 1 — Executive overview
- KPI cards: Revenue, Orders, AOV, Margin %, Loyalty Revenue % (with YoY deltas)
- Line: monthly revenue with 3-mo trend
- Bar: revenue by store, small multiples by month
- Slicers: date range, store

## Page 2 — Product & basket
- Matrix: category → product with Revenue, Units, Margin % (conditional formatting on margin)
- Bar: top 10 products by gross profit
- Table: top basket pairs from `results/08_market_basket.csv` (import as static table)
- Decomposition tree: Revenue by category → product → store

## Page 3 — Customers
- Cohort retention matrix (import `results/06_cohort_retention.csv`, matrix visual, conditional formatting as heatmap)
- RFM segment cards: customers, avg spend, % of revenue per segment
- Scatter: frequency vs monetary, colored by segment (customer-level RFM export)

## Page 4 — Operations
- Heatmap (matrix): hour of day × day of week, Revenue (labor scheduling view)
- Column: hot vs cold revenue by month (seasonality)
- Line: espresso weekly units around the Jan 2026 price change, with reference line

## Build order
1. Model + date table + core measures (30 min)
2. Page 1, get the layout theme right first (1 hr)
3. Pages 2-4 (2-3 hrs)
4. Screenshots into README; publish page 1 rebuild to Tableau Public
