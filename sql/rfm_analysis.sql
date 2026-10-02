-- SQL Query to calculate Customer-Level Recency, Frequency, Monetary and NTILE Quantile Scores
USE ecom_rfm_db;

WITH dynamic_snapshot AS (
    -- Reference snapshot date = max(InvoiceDate) + 1 day
    SELECT DATE_ADD(MAX(InvoiceDate), INTERVAL 1 DAY) AS snapshot_date
    FROM cleaned_transactions
),
customer_rfm_raw AS (
    SELECT 
        t.CustomerID,
        DATEDIFF((SELECT snapshot_date FROM dynamic_snapshot), MAX(t.InvoiceDate)) AS Recency,
        COUNT(DISTINCT t.InvoiceNo) AS Frequency,
        ROUND(SUM(t.Revenue), 2) AS Monetary
    FROM cleaned_transactions t
    GROUP BY t.CustomerID
),
rfm_quantiles AS (
    SELECT 
        CustomerID,
        Recency,
        Frequency,
        Monetary,
        -- Recency: Reverse NTILE (1 = lowest recency / most recent = Score 5)
        NTILE(5) OVER (ORDER BY Recency DESC) AS R_Score,
        NTILE(5) OVER (ORDER BY Frequency ASC) AS F_Score,
        NTILE(5) OVER (ORDER BY Monetary ASC) AS M_Score
    FROM customer_rfm_raw
)
SELECT 
    CustomerID,
    Recency,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    CONCAT(R_Score, F_Score, M_Score) AS RFM_Score,
    (R_Score + F_Score + M_Score) AS RFM_Total_Score,
    CASE 
        WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Champions'
        WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Loyal Customers'
        WHEN M_Score >= 4 THEN 'Big Spenders'
        WHEN R_Score >= 4 AND F_Score IN (2, 3) THEN 'Potential Loyalists'
        WHEN R_Score >= 4 AND F_Score = 1 THEN 'New Customers'
        WHEN R_Score IN (2, 3) AND F_Score IN (2, 3) THEN 'Need Attention'
        WHEN R_Score <= 2 AND (F_Score >= 3 OR M_Score >= 3) THEN 'At Risk'
        WHEN R_Score = 1 AND F_Score <= 2 AND M_Score <= 2 THEN 'Lost Customers'
        ELSE 'Hibernating / Low Value'
    END AS Segment
FROM rfm_quantiles
ORDER BY Monetary DESC;
