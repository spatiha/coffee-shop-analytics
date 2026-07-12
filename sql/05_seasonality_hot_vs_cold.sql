-- Q5: How strong is the hot/cold seasonal swing? (Inventory + menu planning)
-- Techniques: conditional aggregation with FILTER, share calculation

SELECT
    date_trunc('month', t.transaction_ts) AS month,
    ROUND(SUM(oi.quantity * oi.unit_price)
        FILTER (WHERE p.category = 'cold'), 0)     AS cold_drink_revenue,
    ROUND(SUM(oi.quantity * oi.unit_price)
        FILTER (WHERE p.category IN ('espresso', 'brewed', 'tea',
                                     'other_drink')), 0) AS hot_drink_revenue,
    ROUND(100.0 * SUM(oi.quantity * oi.unit_price)
              FILTER (WHERE p.category = 'cold')
        / SUM(oi.quantity * oi.unit_price)
              FILTER (WHERE p.category IN ('cold', 'espresso', 'brewed',
                                           'tea', 'other_drink')), 1)
        AS cold_share_pct
FROM transactions t
JOIN order_items oi USING (transaction_id)
JOIN products p     USING (product_id)
GROUP BY 1
ORDER BY 1;
