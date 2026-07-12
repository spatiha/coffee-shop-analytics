-- Q10: Espresso prices rose ~4% on Jan 6, 2026. Did volume hold?
-- Compares espresso vs unaffected categories around the change (rough diff-in-diff read).
-- Techniques: comparison-group framing, conditional aggregation

WITH weekly AS (
    SELECT
        date_trunc('week', t.transaction_ts) AS week,
        CASE WHEN p.category = 'espresso' THEN 'espresso (price up 4%)'
             ELSE 'all other drinks' END     AS grp,
        SUM(oi.quantity)                     AS units,
        SUM(oi.quantity * oi.unit_price)     AS revenue
    FROM transactions t
    JOIN order_items oi USING (transaction_id)
    JOIN products p     USING (product_id)
    WHERE p.category IN ('espresso', 'brewed', 'cold', 'tea', 'other_drink')
      AND t.transaction_ts BETWEEN DATE '2025-11-01' AND DATE '2026-03-01'
    GROUP BY 1, 2
)
SELECT
    grp,
    CASE WHEN week < DATE '2026-01-06' THEN 'before' ELSE 'after' END AS period,
    ROUND(AVG(units), 0)   AS avg_weekly_units,
    ROUND(AVG(revenue), 0) AS avg_weekly_revenue
FROM weekly
GROUP BY 1, 2
ORDER BY grp, period DESC;
