-- Q4: Which products drive profit (not just revenue)? Best seller per category?
-- Techniques: margin calc, RANK() within category, HAVING

WITH product_perf AS (
    SELECT
        p.category,
        p.product_name,
        SUM(oi.quantity)                                  AS units,
        SUM(oi.quantity * oi.unit_price)                  AS revenue,
        SUM(oi.quantity * (oi.unit_price - p.cost))       AS gross_profit,
        ROUND(100.0 * SUM(oi.quantity * (oi.unit_price - p.cost))
              / SUM(oi.quantity * oi.unit_price), 1)      AS margin_pct
    FROM order_items oi
    JOIN products p USING (product_id)
    GROUP BY 1, 2
    HAVING SUM(oi.quantity) > 100
)
SELECT
    category,
    product_name,
    units,
    ROUND(revenue, 0)      AS revenue,
    ROUND(gross_profit, 0) AS gross_profit,
    margin_pct,
    RANK() OVER (PARTITION BY category ORDER BY gross_profit DESC)
        AS profit_rank_in_category
FROM product_perf
ORDER BY category, profit_rank_in_category;
