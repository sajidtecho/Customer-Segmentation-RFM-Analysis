# Interview Preparation: 20 Common Questions & Answers

### 1. What problem does this project solve?
**Answer**: It solves the problem of unsegmented customer transaction data. E-commerce businesses have massive raw transaction logs but don't know who their most valuable customers are or who is about to churn. This project segments customers using RFM analysis so marketing teams can run targeted retention campaigns.

### 2. Why did you choose RFM analysis?
**Answer**: RFM (Recency, Frequency, Monetary) is a proven, intuitive, and computationally efficient technique in direct marketing and retail analytics. It evaluates customer behavior across three fundamental dimensions without requiring complex black-box assumptions.

### 3. What is Recency?
**Answer**: Recency measures the number of days elapsed between a customer's most recent purchase date and the dataset snapshot reference date. Lower recency indicates higher engagement.

### 4. What is Frequency?
**Answer**: Frequency measures the total number of unique orders/invoices placed by a customer within the analysis time window.

### 5. What is Monetary?
**Answer**: Monetary measures the total cumulative dollar amount spent by a customer on valid purchase transactions.

### 6. Why is Recency reversed during scoring?
**Answer**: In RFM scoring (1-5), a higher score represents better behavior. Since a lower recency value means a customer purchased more recently (which is better), we reverse the scoring so that lower recency days receive an R_Score of 5.

### 7. Why did you use unique InvoiceNo for Frequency instead of total items?
**Answer**: Total item count reflects quantity per cart rather than distinct purchasing decisions. Counting unique `InvoiceNo` accurately reflects how many times a customer chose to visit and complete a transaction.

### 8. How did you handle cancelled orders?
**Answer**: Invoices starting with "C" represent cancellations and return orders. I filtered out cancelled transactions from the main purchase dataset to prevent artificial negative revenue distortion during RFM scoring.

### 9. How did you handle missing CustomerID?
**Answer**: Rows with missing `CustomerID` (135,037 rows) represent guest checkouts or unauthenticated users. Since RFM analysis requires tracking individual customer identity, these rows were excluded from customer-level RFM scoring.

### 10. Why did you use quantile-based scoring (qcut)?
**Answer**: Quantile binning divides customers into equal-sized groups (20% of customers per score from 1 to 5), ensuring a balanced score distribution regardless of raw feature scales.

### 11. What problems can occur with `qcut` and how did you solve them?
**Answer**: When a dataset has many identical values (e.g., many customers with Frequency = 1), `qcut` throws a `ValueError: Bin edges must be unique`. I solved this by applying `rank(method='first')` before `qcut`, ensuring unique ordinal ranks.

### 12. Why did you use K-Means clustering?
**Answer**: K-Means is an unsupervised machine learning algorithm that groups customers based on spatial distance in mathematical feature space, providing an unbiased data-driven complement to rule-based RFM scoring.

### 13. Why did you standardize the features before clustering?
**Answer**: RFM metrics have vastly different scales (Recency in days: 1-373, Frequency: 1-200+, Monetary: $1-$280,000+). Without standardization (StandardScaler), K-Means distance calculations would be completely dominated by Monetary values.

### 14. How did you choose K for K-Means?
**Answer**: I evaluated $K$ from 2 to 8 using the Elbow Method (tracking Inertia reduction) and Silhouette Scores. $K=4$ offered the optimal balance between cluster compactness and business interpretability.

### 15. What is the difference between RFM segmentation and K-Means clustering?
**Answer**: RFM segmentation uses explicit, business-defined quantile rules and score boundaries. K-Means clustering uses unsupervised mathematical distance algorithms (`Euclidean distance` in scaled log space) to discover natural groupings without predefined rules.

### 16. What business actions can be taken for each segment?
**Answer**:
- **Champions**: Offer VIP rewards and early product access.
- **At Risk**: Send automated re-engagement emails with targeted discounts.
- **New Customers**: Send welcome series and post-purchase recommendations.

### 17. What are the limitations of RFM analysis?
**Answer**: RFM looks purely at historical transactions and does not incorporate customer sentiment, browsing behavior, demographics, or predictive future trends.

### 18. How would you deploy this in a production environment?
**Answer**: I would schedule `main.py` as an automated Airflow / Cron pipeline reading from a SQL data warehouse (Snowflake / BigQuery), refreshing RFM tables daily, and rendering the updated metrics on a Streamlit or Tableau dashboard.

### 19. How would you handle new customers?
**Answer**: New customers start with Recency based on their first order date and Frequency = 1. They are placed in the "New Customers" segment until sufficient transaction history accumulates for next-month re-scoring.

### 20. How would you update the segmentation periodically?
**Answer**: By maintaining dynamic reference date calculation (`snapshot_date = max(InvoiceDate) + 1 day`), the entire pipeline runs reproducibly on new monthly transaction snapshots without manual code modification.
