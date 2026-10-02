-- MySQL Business Analytics Queries for Customer Segmentation & RFM Project
USE ecom_rfm_db;

-- Query 1: Total Revenue
SELECT ROUND(SUM(Revenue), 2) AS total_revenue
FROM cleaned_transactions;

-- Query 2: Total Orders
SELECT COUNT(DISTINCT InvoiceNo) AS total_orders
FROM cleaned_transactions;

-- Query 3: Unique Customers
SELECT COUNT(DISTINCT CustomerID) AS unique_customers
FROM cleaned_transactions;

-- Query 4: Average Order Value (AOV)
SELECT ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM cleaned_transactions;

-- Query 5: Revenue by Country
SELECT 
    Country,
    COUNT(DISTINCT CustomerID) AS customer_count,
    COUNT(DISTINCT InvoiceNo) AS order_count,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM cleaned_transactions
GROUP BY Country
ORDER BY total_revenue DESC;

-- Query 6: Top 10 Customers by Revenue
SELECT 
    CustomerID,
    COUNT(DISTINCT InvoiceNo) AS order_count,
    SUM(Quantity) AS total_units_bought,
    ROUND(SUM(Revenue), 2) AS total_spent
FROM cleaned_transactions
GROUP BY CustomerID
ORDER BY total_spent DESC
LIMIT 10;

-- Query 7: Customers with Highest Order Frequency
SELECT 
    CustomerID,
    COUNT(DISTINCT InvoiceNo) AS order_frequency,
    ROUND(SUM(Revenue), 2) AS total_spent
FROM cleaned_transactions
GROUP BY CustomerID
ORDER BY order_frequency DESC
LIMIT 10;

-- Query 8: Monthly Revenue Trend
SELECT 
    InvoiceMonthYear,
    COUNT(DISTINCT InvoiceNo) AS monthly_orders,
    ROUND(SUM(Revenue), 2) AS monthly_revenue
FROM cleaned_transactions
GROUP BY InvoiceMonthYear
ORDER BY InvoiceMonthYear ASC;

-- Query 9: Customer-Level Recency (Days since last purchase)
SELECT 
    CustomerID,
    MAX(InvoiceDate) AS last_purchase_date,
    DATEDIFF((SELECT DATE_ADD(MAX(InvoiceDate), INTERVAL 1 DAY) FROM cleaned_transactions), MAX(InvoiceDate)) AS recency_days
FROM cleaned_transactions
GROUP BY CustomerID
ORDER BY recency_days ASC;

-- Query 10: Customer-Level Frequency
SELECT 
    CustomerID,
    COUNT(DISTINCT InvoiceNo) AS total_orders
FROM cleaned_transactions
GROUP BY CustomerID
ORDER BY total_orders DESC;

-- Query 11: Customer-Level Monetary
SELECT 
    CustomerID,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM cleaned_transactions
GROUP BY CustomerID
ORDER BY total_revenue DESC;

-- Query 12: Segment-Level Revenue Breakdown
SELECT 
    Segment,
    COUNT(CustomerID) AS customer_count,
    ROUND(SUM(Monetary), 2) AS segment_revenue,
    ROUND(AVG(Monetary), 2) AS avg_monetary,
    ROUND(AVG(Recency), 1) AS avg_recency,
    ROUND(AVG(Frequency), 2) AS avg_frequency
FROM customer_segments
GROUP BY Segment
ORDER BY segment_revenue DESC;

-- Query 13: Segment-Level Customer Count & Percentage
SELECT 
    Segment,
    COUNT(CustomerID) AS customer_count,
    ROUND(COUNT(CustomerID) * 100.0 / (SELECT COUNT(*) FROM customer_segments), 2) AS customer_percentage
FROM customer_segments
GROUP BY Segment
ORDER BY customer_count DESC;

-- Query 14: At-Risk Customers (High Spending / Frequency but long inactive time)
SELECT 
    CustomerID,
    Recency,
    Frequency,
    Monetary,
    Segment
FROM customer_segments
WHERE Segment = 'At Risk'
ORDER BY Monetary DESC;

-- Query 15: Top 10 Best-Selling Products by Revenue
SELECT 
    StockCode,
    Description,
    SUM(Quantity) AS total_quantity_sold,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM cleaned_transactions
GROUP BY StockCode, Description
ORDER BY total_revenue DESC
LIMIT 10;
