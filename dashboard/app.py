"""
Streamlit Interactive Analytics Dashboard for Customer Segmentation & RFM Project.
Runs interactive visualization powered by Plotly and Pandas.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set Page Config
st.set_page_config(
    page_title="Customer Segmentation & RFM Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Professional Analytics Layout
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent
    tx_file = base_dir / "data" / "processed" / "cleaned_transactions.csv"
    seg_file = base_dir / "data" / "processed" / "customer_segments.csv"

    if not tx_file.exists() or not seg_file.exists():
        st.error("Processed data files not found! Please run 'python main.py' first.")
        st.stop()

    df_tx = pd.read_csv(tx_file)
    df_tx["InvoiceDate"] = pd.to_datetime(df_tx["InvoiceDate"])
    df_seg = pd.read_csv(seg_file)
    return df_tx, df_seg

df_tx, df_seg = load_data()

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🔍 Dashboard Filters")

# Country Filter
countries = ["All"] + sorted(df_tx["Country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country:", countries, index=0)

# Segment Filter
segments = ["All"] + sorted(df_seg["Segment"].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox("Select Customer Segment:", segments, index=0)

# Date Range Filter
min_date = df_tx["InvoiceDate"].min().date()
max_date = df_tx["InvoiceDate"].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter Data
filtered_tx = df_tx.copy()
filtered_seg = df_seg.copy()

if selected_country != "All":
    filtered_tx = filtered_tx[filtered_tx["Country"] == selected_country]
    valid_custs = filtered_tx["CustomerID"].unique()
    filtered_seg = filtered_seg[filtered_seg["CustomerID"].isin(valid_custs)]

if selected_segment != "All":
    filtered_seg = filtered_seg[filtered_seg["Segment"] == selected_segment]
    valid_custs = filtered_seg["CustomerID"].unique()
    filtered_tx = filtered_tx[filtered_tx["CustomerID"].isin(valid_custs)]

filtered_tx = filtered_tx[
    (filtered_tx["InvoiceDate"].dt.date >= start_date) &
    (filtered_tx["InvoiceDate"].dt.date <= end_date)
]

# =========================================================
# HEADER & EXECUTIVE KPI CARDS
# =========================================================
st.markdown('<div class="main-header">Customer Segmentation & RFM Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Executive Dashboard for E-Commerce Transaction Analysis & Customer Segmentation</div>', unsafe_allow_html=True)

# Metrics Calculation
total_revenue = filtered_tx["Revenue"].sum()
total_customers = filtered_seg["CustomerID"].nunique()
total_orders = filtered_tx["InvoiceNo"].nunique()
aov = total_revenue / total_orders if total_orders > 0 else 0
avg_cust_rev = total_revenue / total_customers if total_customers > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Customers", f"{total_customers:,}")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Average Order Value", f"${aov:,.2f}")
col5.metric("Avg Revenue / Customer", f"${avg_cust_rev:,.2f}")

st.divider()

# =========================================================
# SECTION 1: EXECUTIVE OVERVIEW
# =========================================================
st.subheader("📈 Executive Overview")
c1, c2 = st.columns(2)

with c1:
    monthly_rev = filtered_tx.groupby("InvoiceMonthYear")["Revenue"].sum().reset_index()
    fig_month = px.line(
        monthly_rev, x="InvoiceMonthYear", y="Revenue",
        title="Monthly Revenue Trend",
        labels={"InvoiceMonthYear": "Month-Year", "Revenue": "Revenue ($)"},
        markers=True, color_discrete_sequence=["#2563EB"]
    )
    fig_month.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_month, use_container_width=True)

with c2:
    country_rev = filtered_tx.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_country = px.bar(
        country_rev, x="Revenue", y="Country", orientation="h",
        title="Top 10 Countries by Revenue ($)",
        labels={"Revenue": "Total Revenue ($)", "Country": "Country"},
        color="Revenue", color_continuous_scale="Blues"
    )
    fig_country.update_layout(template="plotly_white", yaxis=dict(autorange="reversed"), margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_country, use_container_width=True)

# =========================================================
# SECTION 2: RFM ANALYSIS & DISTRIBUTIONS
# =========================================================
st.subheader("📊 RFM Metrics Distribution")
r1, r2, r3 = st.columns(3)

with r1:
    fig_r = px.histogram(filtered_seg, x="Recency", nbins=30, title="Recency Distribution (Days)", color_discrete_sequence=["#3B82F6"])
    fig_r.update_layout(template="plotly_white")
    st.plotly_chart(fig_r, use_container_width=True)

with r2:
    fig_f = px.histogram(filtered_seg, x="Frequency", nbins=30, title="Frequency Distribution (Orders)", color_discrete_sequence=["#10B981"], log_y=True)
    fig_f.update_layout(template="plotly_white")
    st.plotly_chart(fig_f, use_container_width=True)

with r3:
    fig_m = px.histogram(filtered_seg, x="Monetary", nbins=30, title="Monetary Distribution ($)", color_discrete_sequence=["#EF4444"], log_y=True)
    fig_m.update_layout(template="plotly_white")
    st.plotly_chart(fig_m, use_container_width=True)

# =========================================================
# SECTION 3: CUSTOMER SEGMENTATION BREAKDOWN
# =========================================================
st.subheader("🎯 Customer Segment Breakdown")
s1, s2 = st.columns(2)

seg_summary = filtered_seg.groupby("Segment").agg(
    Customer_Count=("CustomerID", "count"),
    Total_Revenue=("Monetary", "sum"),
    Avg_Monetary=("Monetary", "mean"),
    Avg_Recency=("Recency", "mean")
).reset_index()

with s1:
    fig_seg_count = px.pie(
        seg_summary, names="Segment", values="Customer_Count",
        title="Customer Distribution by Segment",
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_seg_count.update_layout(template="plotly_white")
    st.plotly_chart(fig_seg_count, use_container_width=True)

with s2:
    fig_seg_rev = px.bar(
        seg_summary.sort_values(by="Total_Revenue", ascending=False),
        x="Segment", y="Total_Revenue", text_auto=".2s",
        title="Revenue Contribution by Customer Segment ($)",
        color="Segment", color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_seg_rev.update_layout(template="plotly_white", xaxis_tickangle=-45)
    st.plotly_chart(fig_seg_rev, use_container_width=True)

# =========================================================
# SECTION 4: INTERACTIVE CUSTOMER DETAILS TABLE
# =========================================================
st.subheader("📋 Customer Details Explorer")
table_cols = ["CustomerID", "Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score", "RFM_Score", "RFM_Total_Score", "Segment", "Cluster_Label"]
st.dataframe(
    filtered_seg[table_cols].sort_values(by="Monetary", ascending=False),
    use_container_width=True,
    height=350
)

# =========================================================
# SECTION 5: AUTOMATED BUSINESS INSIGHTS
# =========================================================
st.subheader("💡 Key Business Insights")
top_seg = seg_summary.sort_values(by="Total_Revenue", ascending=False).iloc[0]
most_pop_seg = seg_summary.sort_values(by="Customer_Count", ascending=False).iloc[0]

st.markdown(f"""
- **Top Revenue Segment**: **{top_seg['Segment']}** generates **${top_seg['Total_Revenue']:,.2f}** ({ (top_seg['Total_Revenue']/total_revenue*100):.1f}% of total revenue).
- **Largest Customer Group**: **{most_pop_seg['Segment']}** contains **{most_pop_seg['Customer_Count']:,} customers** ({ (most_pop_seg['Customer_Count']/total_customers*100):.1f}% of customer base).
- **At-Risk Analysis**: Customers in the **At Risk** segment haven't purchased in over **200 days** on average despite high historical spending. Re-engagement campaigns are recommended.
""")
