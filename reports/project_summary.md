# Project Summary: Customer Segmentation & RFM Analytics for E-Commerce

## 1. Business Problem
An online e-commerce retailer with thousands of daily transactions struggled to understand customer purchasing patterns, retention rates, and revenue concentration. Without structured segmentation, marketing efforts were non-targeted, leading to high acquisition costs and customer churn among high-value accounts.

## 2. Dataset Overview
- **Source**: UCI Machine Learning Repository (Online Retail Dataset)
- **Time Range**: December 1, 2010 to December 9, 2011 (1 year)
- **Raw Size**: 541,909 transactions across 38 countries and 4,372 unique customers.

## 3. Data Cleaning Pipeline
- **Initial Raw Transactions**: 541,909
- **Duplicate Rows Removed**: 5,268
- **Missing CustomerID Removed**: 135,037
- **Cancelled Transactions Removed (InvoiceNo 'C')**: 8,872
- **Zero / Negative UnitPrice Removed**: 40
- **Final Cleaned Transactions**: 392,692 rows (72.46% retained)
- **Cleaned Unique Customers**: 4,338

## 4. Exploratory Data Analysis (EDA)
- **Total Revenue Analyzed**: $8,887,208.89
- **Average Order Value (AOV)**: $479.56
- **Average Customer Revenue**: $2,048.69
- **Top Geographic Market**: United Kingdom ($7,308,391.55 revenue, 82.2% of total). Top international markets include Netherlands, EIRE, Germany, and France.

## 5. RFM Methodology
- **Snapshot Date**: `2011-12-10 12:50:00` (Calculated dynamically as `max(InvoiceDate) + 1 day`)
- **Recency**: Days elapsed between snapshot date and customer's last purchase.
- **Frequency**: Total count of unique `InvoiceNo` orders per customer.
- **Monetary**: Sum of `Revenue` (`Quantity` * `UnitPrice`) per customer.
- **Scoring**: 1 to 5 scale calculated using quantile ranking (`pd.qcut` combined with `rank(method='first')`).

## 6. Rule-Based Customer Segmentation
Customers were assigned to 9 business segments:
1. **Champions**: 942 customers (21.7%) | $5,737,952.12 Revenue (64.56%) | Avg Recency: 12.5 days | Avg Frequency: 11.2 orders
2. **Loyal Customers**: 767 customers (17.7%) | $1,426,427.13 Revenue (16.05%) | Avg Recency: 35.1 days | Avg Frequency: 4.2 orders
3. **Big Spenders**: 413 customers (9.5%) | $959,287.36 Revenue (10.79%) | Avg Recency: 125.1 days | Avg Frequency: 3.4 orders
4. **Need Attention**: 579 customers (13.3%) | $226,126.89 Revenue (2.54%) | Avg Recency: 91.7 days
5. **At Risk**: 342 customers (7.9%) | $188,561.42 Revenue (2.12%) | Avg Recency: 204.0 days
6. **Lost Customers**: 555 customers (12.8%) | $124,745.70 Revenue (1.40%) | Avg Recency: 279.2 days
7. **Hibernating / Low Value**: 346 customers (8.0%) | $100,885.24 Revenue (1.14%)
8. **Potential Loyalists**: 260 customers (6.0%) | $84,591.83 Revenue (0.95%)
9. **New Customers**: 134 customers (3.1%) | $38,631.20 Revenue (0.43%)

## 7. Machine Learning K-Means Clustering
- **Feature Preprocessing**: `log1p` transformation to resolve extreme right-skewness, followed by `StandardScaler`.
- **Optimal K Evaluation**: Evaluated $K \in [2, 8]$. Selected $K=4$ based on Elbow Method inertia curvature and Silhouette score ($0.3375$).
- **Cluster Profiles**:
  - **Cluster 0**: High-Spender VIPs (Frequent buyers with highest total spending).
  - **Cluster 1**: Active Moderate Buyers.
  - **Cluster 2**: Occasional Low-Spenders.
  - **Cluster 3**: Dormant / Inactive Accounts.

## 8. SQL Database Integration
Created MySQL-compatible database scripts (`sql/schema.sql`, `sql/rfm_analysis.sql`, `sql/business_queries.sql`) containing 15 analytical queries for executive reporting.

## 9. Interactive Analytics Dashboard
Built a Streamlit dashboard (`dashboard/app.py`) featuring Plotly charts, executive KPI cards, country/segment/date filters, RFM score distributions, and customer detail tables.

## 10. Key Business Findings
- **High Revenue Concentration**: The top 21.7% of customers (Champions) contribute 64.56% ($5.74M) of total revenue.
- **At-Risk Opportunity**: 342 high-value customers have gone inactive for over 200 days on average, representing $188.5K in past spending. Win-back campaigns could reactivate a significant revenue stream.
- **Low Repeat Rate in New Cohorts**: 12.8% of customers are Lost after making only 1 purchase. Improving onboarding and 30-day post-purchase engagement will boost retention.

## 11. Project Limitations
- Dataset covers 1 year of sales, preventing multi-year cohort analysis.
- Demographic variables (age, gender, income) were not included in the raw transaction dataset.

## 12. Future Work
- Integrate Predictive Customer Lifetime Value (CLV) using `Lifetimes` BG/NBD models.
- Build automated email trigger integrations for At-Risk and Champion segments.
