-- Q3: How do the three stores compare, adjusting for their different sizes?
-- Techniques: multi-join aggregation, YoY comparison with LAG partitioned by store

WITH store_month AS (
    SELECT
        s.store_name,
        date_trunc('month', t.transaction_ts)  AS month,
        SUM(oi.quantity * oi.unit_price)       AS revenue,
        COUNT(DISTINCT t.transaction_id)       AS orders,
        COUNT(DISTINCT t.customer_id)          AS unique_customers
    FROM transactions t
    JOIN order_items oi USING (transaction_id)
    JOIN stores s      USING (store_id)
    GROUP BY 1, 2
)
SELECT
    store_name,
    month,
    ROUND(revenue, 0)  AS revenue,
    orders,
    unique_customers,
    ROUND(revenue / orders, 2) AS aov,
    ROUND(100.0 * (revenue - LAG(revenue, 12) OVER
        (PARTITION BY store_name ORDER BY month))
        / LAG(revenue, 12) OVER
        (PARTITION BY store_name ORDER BY month), 1) AS yoy_growth_pct
FROM store_month
ORDER BY store_name, month;
