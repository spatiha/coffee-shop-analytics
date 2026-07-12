-- Q7: Which customers are worth targeted marketing? RFM segmentation.
-- Techniques: NTILE quintiles, multi-CTE pipeline, CASE-based segment labels

WITH customer_rfm AS (
    SELECT
        t.customer_id,
        datediff('day', MAX(t.transaction_ts), DATE '2026-06-30') AS recency_days,
        COUNT(DISTINCT t.transaction_id)                          AS frequency,
        SUM(oi.quantity * oi.unit_price)                          AS monetary
    FROM transactions t
    JOIN order_items oi USING (transaction_id)
    GROUP BY 1
),
scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency)         AS f_score,
        NTILE(5) OVER (ORDER BY monetary)          AS m_score
    FROM customer_rfm
),
labeled AS (
    SELECT *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 THEN 'champions'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'promising_new'
            WHEN r_score <= 2 AND f_score >= 4 THEN 'at_risk_regulars'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'lost'
            ELSE 'steady'
        END AS rfm_segment
    FROM scored
)
SELECT
    rfm_segment,
    COUNT(*)                        AS customers,
    ROUND(AVG(recency_days), 0)     AS avg_recency_days,
    ROUND(AVG(frequency), 1)        AS avg_orders,
    ROUND(AVG(monetary), 0)         AS avg_lifetime_spend,
    ROUND(SUM(monetary), 0)         AS total_spend,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1)
        AS pct_of_revenue
FROM labeled
GROUP BY 1
ORDER BY total_spend DESC;
