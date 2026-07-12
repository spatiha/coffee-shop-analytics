-- Q1: How is the business trending month over month?
-- Techniques: CTE, window functions (LAG, moving average via frame clause)

WITH monthly AS (
    SELECT
        date_trunc('month', t.transaction_ts) AS month,
        COUNT(DISTINCT t.transaction_id)      AS orders,
        SUM(oi.quantity * oi.unit_price)      AS revenue,
        SUM(oi.quantity * oi.unit_price)
            / COUNT(DISTINCT t.transaction_id) AS avg_order_value
    FROM transactions t
    JOIN order_items oi USING (transaction_id)
    GROUP BY 1
)
SELECT
    month,
    orders,
    ROUND(revenue, 0)                                        AS revenue,
    ROUND(avg_order_value, 2)                                AS aov,
    ROUND(100.0 * (revenue - LAG(revenue) OVER w)
          / LAG(revenue) OVER w, 1)                          AS mom_growth_pct,
    ROUND(AVG(revenue) OVER (ORDER BY month
          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0)      AS revenue_3mo_avg
FROM monthly
WINDOW w AS (ORDER BY month)
ORDER BY month;
