-- Q6: Do customers stick around? Monthly signup cohorts and their return rates.
-- Techniques: cohort assignment via MIN() window, date arithmetic, pivot-style output

WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(date_trunc('month', transaction_ts)) AS cohort_month
    FROM transactions
    GROUP BY 1
),
activity AS (
    SELECT DISTINCT
        t.customer_id,
        fp.cohort_month,
        datediff('month', fp.cohort_month,
                 date_trunc('month', t.transaction_ts)) AS months_since_first
    FROM transactions t
    JOIN first_purchase fp USING (customer_id)
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM first_purchase GROUP BY 1
)
SELECT
    a.cohort_month,
    cs.cohort_customers,
    a.months_since_first,
    COUNT(DISTINCT a.customer_id)                          AS active_customers,
    ROUND(100.0 * COUNT(DISTINCT a.customer_id)
          / cs.cohort_customers, 1)                        AS retention_pct
FROM activity a
JOIN cohort_size cs USING (cohort_month)
WHERE a.months_since_first BETWEEN 0 AND 12
GROUP BY 1, 2, 3
ORDER BY 1, 3;
