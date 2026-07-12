-- Q9: Did the loyalty program (launched Aug 2025) change member behavior?
-- Before/after comparison within the same customers, so each member is their own control.
-- Techniques: date-anchored self-comparison, per-customer normalization

WITH member_windows AS (
    SELECT
        c.customer_id,
        c.loyalty_join_date,
        -- observation windows: 90 days before vs 90 days after joining
        CASE
            WHEN t.transaction_ts::date BETWEEN c.loyalty_join_date - 90
                 AND c.loyalty_join_date - 1 THEN 'before'
            WHEN t.transaction_ts::date BETWEEN c.loyalty_join_date
                 AND c.loyalty_join_date + 89 THEN 'after'
        END AS obs_window,
        t.transaction_id,
        SUM(oi.quantity * oi.unit_price) AS order_value
    FROM customers c
    JOIN transactions t USING (customer_id)
    JOIN order_items oi USING (transaction_id)
    WHERE c.loyalty_join_date IS NOT NULL
      AND c.loyalty_join_date BETWEEN DATE '2025-10-01' AND DATE '2026-03-31'
    GROUP BY 1, 2, 3, 4
)
SELECT
    obs_window,
    COUNT(DISTINCT customer_id)             AS members,
    COUNT(transaction_id)                   AS orders,
    ROUND(COUNT(transaction_id) * 1.0
          / COUNT(DISTINCT customer_id), 1) AS orders_per_member_90d,
    ROUND(AVG(order_value), 2)              AS avg_order_value
FROM member_windows
WHERE obs_window IS NOT NULL
GROUP BY 1
ORDER BY obs_window DESC;
