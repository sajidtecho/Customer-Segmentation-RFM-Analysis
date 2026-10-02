# Customer Segmentation & RFM Analytics for E-Commerce

An end-to-end, industry-oriented customer analytics and machine learning solution built on historical transaction data from the UCI Online Retail dataset.

---

## 📌 Business Problem
An e-commerce retailer with hundreds of thousands of transactions lacked clear visibility into customer purchasing behaviors, customer retention dynamics, and revenue concentration. Marketing campaigns were executed uniformly across all customers, leading to inefficient ad spend, high customer acquisition costs, and unmitigated churn among high-value accounts.

## 🎯 Project Objective
1. Clean and process raw e-commerce transaction logs (541K+ rows).
2. Engineer transaction features (Revenue, temporal components).
3. Compute **Recency, Frequency, and Monetary (RFM)** metrics and 1–5 score distributions.
4. Segment 4,338 unique customers into 9 distinct business categories.
5. Train an unsupervised **K-Means Clustering** model ($K=4$) for data-driven ML segmentation.
6. Provide a MySQL relational database schema with 15 production analytical queries.
7. Build an interactive **Streamlit & Plotly** executive analytics dashboard.

---

## 📊 Dataset & Data Dictionary
- **Source**: UCI Online Retail Dataset (`data/raw/Online Retail.xlsx`)
- **Timeframe**: December 1, 2010 – December 9, 2011 (1 Year)
- **Raw Volume**: 541,909 rows | 38 countries | 4,372 customers

### Data Dictionary
| Column Name | Data Type | Business Description |
| :--- | :--- | :--- |
| **InvoiceNo** | String | 6-digit integer assigned to each transaction. If starts with 'C', indicates a cancellation. |
| **StockCode** | String | 5-digit product code uniquely assigned to a distinct item. |
| **Description** | String | Product / item name description. |
| **Quantity** | Integer | Quantities of each product per transaction. |
| **InvoiceDate** | Datetime | The day and time when a transaction was generated. |
| **UnitPrice** | Float | Product price per unit in Sterling (£). |
| **CustomerID** | Integer | 5-digit customer number uniquely assigned to each registered customer. |
| **Country** | String | Name of the country where customer resides. |

---

## 🛠️ Tech Stack
- **Language**: Python 3.11+
- **Data Wrangling**: `pandas`, `numpy`
- **Visualization**: `matplotlib`, `seaborn`, `plotly`
- **Machine Learning**: `scikit-learn` (K-Means, StandardScaler, Silhouette Evaluation)
- **Database & SQL**: `sqlalchemy`, `pymysql`, MySQL dialect
- **Interactive Dashboard**: `streamlit`, `plotly`
- **Testing**: `pytest`

---

## 🧹 Data Cleaning Pipeline
- **Raw Rows**: 541,909
- **Duplicates Removed**: 5,268
- **Missing CustomerIDs Removed**: 135,037 (guest checkouts)
- **Cancellations Removed (`InvoiceNo` starting with 'C')**: 8,872
- **Invalid Prices Removed (`UnitPrice <= 0`)**: 40
- **Cleaned Dataset**: 392,692 rows (72.46% retained) | 4,338 unique customers

---

## 📈 RFM Methodology
- **Snapshot Reference Date**: `2011-12-10 12:50:00` (Calculated dynamically as `max(InvoiceDate) + 1 day`).
- **Recency (R)**: Days since last purchase relative to snapshot date.
- **Frequency (F)**: Count of unique `InvoiceNo` orders per customer.
- **Monetary (M)**: Sum of valid customer `Revenue` (`Quantity` * `UnitPrice`).

### Quantile Scoring (1 to 5)
Using `pd.qcut` combined with `rank(method='first')`:
- **R_Score**: 5 (most recent) to 1 (least recent) — *Reversed*.
- **F_Score**: 1 (lowest frequency) to 5 (highest frequency).
- **M_Score**: 1 (lowest total spending) to 5 (highest total spending).

---

## 🎯 Customer Segmentation Rules & Actual Distribution

All values below are calculated directly from the cleaned dataset:

| Segment | Rules (R, F, M Scores) | Customers | Customer % | Total Revenue ($) | Revenue % | Avg Recency | Avg Frequency | Avg Monetary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Champions** | $R \ge 4, F \ge 4, M \ge 4$ | 942 | 21.72% | $5,737,952.12 | 64.56% | 12.5 days | 11.20 | $6,091.24 |
| **Loyal Customers** | $R \ge 3, F \ge 3, M \ge 3$ | 767 | 17.68% | $1,426,427.13 | 16.05% | 35.1 days | 4.16 | $1,859.75 |
| **Big Spenders** | $M \ge 4$ | 413 | 9.52% | $959,287.36 | 10.79% | 125.1 days | 3.42 | $2,322.73 |
| **Need Attention** | $R \in [2,3], F \in [2,3]$ | 579 | 13.35% | $226,126.89 | 2.54% | 91.7 days | 1.65 | $390.55 |
| **At Risk** | $R \le 2, F \ge 3 \lor M \ge 3$ | 342 | 7.88% | $188,561.42 | 2.12% | 204.0 days | 2.37 | $551.35 |
| **Lost Customers** | $R = 1, F \le 2, M \le 2$ | 555 | 12.79% | $124,745.70 | 1.40% | 279.2 days | 1.03 | $224.77 |
| **Hibernating / Low Value** | $R \le 3, F \le 2$ | 346 | 7.98% | $100,885.24 | 1.14% | 76.6 days | 1.35 | $291.58 |
| **Potential Loyalists** | $R \ge 4, F \in [2,3]$ | 260 | 5.99% | $84,591.83 | 0.95% | 16.8 days | 1.70 | $325.35 |
| **New Customers** | $R \ge 4, F = 1$ | 134 | 3.09% | $38,631.20 | 0.43% | 18.1 days | 1.00 | $288.29 |

---

## 🤖 Machine Learning Clustering (K-Means)
- Preprocessing: `log1p` transformation to reduce extreme right-skewness + `StandardScaler`.
- Cluster selection: Evaluated $K \in [2, 8]$ using Elbow Method and Silhouette Score ($0.3375$ at $K=4$).
- Profiles:
  - **Cluster 0**: High-Value VIPs
  - **Cluster 1**: Active Frequent Buyers
  - **Cluster 2**: Occasional Low-Spenders
  - **Cluster 3**: Inactive / Dormant Accounts

---

## 💡 Key Business Insights
1. **Revenue Concentration**: Top 21.7% of customers (Champions) generate **64.56%** ($5.74M) of total company revenue.
2. **At-Risk Value**: 342 At-Risk customers have been inactive for **204 days** on average despite spending $188.5K historically.
3. **Geographic Dominance**: United Kingdom accounts for **82.2%** ($7.31M) of revenue.

---

## 📁 Project Structure
```
Customer-Segmentation-RFM-Analysis/
│
├── data/
│   ├── raw/                      # Raw dataset (Online Retail.xlsx)
│   └── processed/                # Cleaned CSVs (cleaned_transactions.csv, rfm_customers.csv, customer_segments.csv)
│
├── notebooks/                    # Executable Jupyter Notebooks (01 to 05)
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_rfm_analysis.ipynb
│   └── 05_customer_clustering.ipynb
│
├── src/                          # Modular Python package
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── rfm_analysis.py
│   ├── segmentation.py
│   ├── clustering.py
│   └── utils.py
│
├── sql/                          # MySQL database scripts
│   ├── schema.sql
│   ├── rfm_analysis.sql
│   └── business_queries.sql
│
├── dashboard/
│   └── app.py                    # Streamlit interactive analytics dashboard
│
├── reports/
│   ├── figures/                  # Exported charts (monthly_revenue.png, etc.)
│   ├── project_summary.md
│   ├── business_insights.md
│   ├── resume_metrics.md
│   ├── resume_bullets.md
│   └── interview_questions.md
│
├── tests/                        # Pytest suite
│   ├── test_cleaning.py
│   ├── test_rfm.py
│   └── test_segmentation.py
│
├── requirements.txt
├── README.md
└── main.py                       # Master execution pipeline
```

---

## 🚀 How to Run the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline
```bash
python main.py
```

### 3. Run Unit Tests
```bash
python -m pytest
```

### 4. Launch the Interactive Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 🔮 Future Improvements
- Implement BG/NBD and Gamma-Gamma models for predictive Customer Lifetime Value (CLV).
- Add real-time SQL sync with Snowflake or BigQuery.
- Build automated email trigger integrations for At-Risk segments.
