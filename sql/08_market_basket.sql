-- Q8: What sells together? Product affinity for bundling / register placement.
-- Techniques: self-join basket analysis, support / confidence / lift

WITH basket AS (
    SELECT DISTINCT transaction_id, product_id
    FROM order_items
),
n_orders AS (
    SELECT COUNT(DISTINCT transaction_id) AS total FROM transactions
),
product_freq AS (
    SELECT product_id, COUNT(*) AS orders_with
    FROM basket GROUP BY 1
),
pairs AS (
    SELECT
        a.product_id AS product_a,
        b.product_id AS product_b,
        COUNT(*)     AS together
    FROM basket a
    JOIN basket b ON a.transaction_id = b.transaction_id
                 AND a.product_id < b.product_id
    GROUP BY 1, 2
    HAVING COUNT(*) >= 500
)
SELECT
    pa.product_name                                     AS product_a,
    pb.product_name                                     AS product_b,
    pr.together                                         AS orders_together,
    ROUND(100.0 * pr.together / fa.orders_with, 1)      AS confidence_a_to_b_pct,
    ROUND((1.0 * pr.together / n.total)
        / ((1.0 * fa.orders_with / n.total)
         * (1.0 * fb.orders_with / n.total)), 2)        AS lift
FROM pairs pr
JOIN product_freq fa ON pr.product_a = fa.product_id
JOIN product_freq fb ON pr.product_b = fb.product_id
JOIN products pa     ON pr.product_a = pa.product_id
JOIN products pb     ON pr.product_b = pb.product_id
CROSS JOIN n_orders n
ORDER BY lift DESC
LIMIT 15;
