-- Q2: When does revenue actually happen? Where should labor hours go?
-- Techniques: CASE bucketing, window function for share-of-total

WITH orders_by_daypart AS (
    SELECT
        CASE WHEN dayofweek(t.transaction_ts) IN (0, 6)
             THEN 'weekend' ELSE 'weekday' END AS day_type,
        CASE
            WHEN hour(t.transaction_ts) BETWEEN 6  AND 9  THEN '1_morning_rush'
            WHEN hour(t.transaction_ts) BETWEEN 10 AND 11 THEN '2_mid_morning'
            WHEN hour(t.transaction_ts) BETWEEN 12 AND 14 THEN '3_lunch'
            WHEN hour(t.transaction_ts) BETWEEN 15 AND 16 THEN '4_afternoon'
            ELSE '5_evening'
        END AS daypart,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        COUNT(DISTINCT t.transaction_id) AS orders
    FROM transactions t
    JOIN order_items oi USING (transaction_id)
    GROUP BY 1, 2
)
SELECT
    day_type,
    daypart,
    orders,
    ROUND(revenue, 0) AS revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY day_type), 1)
        AS pct_of_daytype_revenue
FROM orders_by_daypart
ORDER BY day_type, daypart;
