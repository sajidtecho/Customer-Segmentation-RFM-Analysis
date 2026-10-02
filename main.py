"""
Main Execution Pipeline for Customer Segmentation & RFM Analytics.
Reproducible, modular pipeline running raw data cleaning, RFM analysis, segmentation, ML clustering, and figure generation.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils import get_project_root, ensure_directories, setup_logger
from src.data_loader import load_raw_data, inspect_raw_data
from src.data_cleaning import clean_transactions
from src.feature_engineering import add_transaction_features
from src.rfm_analysis import calculate_rfm, calculate_rfm_scores
from src.segmentation import segment_customers
from src.clustering import prepare_clustering_data, evaluate_kmeans_k, apply_kmeans_clustering

logger = setup_logger("main_pipeline")

def run_pipeline():
    logger.info("==========================================")
    logger.info("STARTING CUSTOMER SEGMENTATION RFM PIPELINE")
    logger.info("==========================================")
    
    ensure_directories()
    root = get_project_root()
    processed_dir = root / "data" / "processed"
    figures_dir = root / "reports" / "figures"
    reports_dir = root / "reports"

    # Step 1: Load Raw Data
    df_raw = load_raw_data()
    raw_stats = inspect_raw_data(df_raw)
    logger.info(f"Raw Stats: Rows={raw_stats['num_rows']:,}, Customers={raw_stats['unique_customers']:,}, Invoices={raw_stats['unique_invoices']:,}")

    # Step 2: Clean Transactions
    df_cleaned, cleaning_metrics = clean_transactions(df_raw)

    # Step 3: Add Transaction Features (Revenue, Temporal components)
    df_feat = add_transaction_features(df_cleaned)

    # Save cleaned transaction data
    cleaned_file = processed_dir / "cleaned_transactions.csv"
    df_feat.to_csv(cleaned_file, index=False)
    logger.info(f"Saved cleaned transactions to: {cleaned_file}")

    # Step 4: RFM Calculation & Scoring
    rfm_df, snapshot_date = calculate_rfm(df_feat)
    rfm_scored = calculate_rfm_scores(rfm_df)

    rfm_file = processed_dir / "rfm_customers.csv"
    rfm_scored.to_csv(rfm_file, index=False)
    logger.info(f"Saved RFM customer data to: {rfm_file}")

    # Step 5: Rule-based Customer Segmentation
    df_segmented, segment_summary = segment_customers(rfm_scored)

    # Step 6: Machine Learning K-Means Clustering
    X_scaled, scaler, rfm_log = prepare_clustering_data(df_segmented)
    k_eval_df = evaluate_kmeans_k(X_scaled, k_range=range(2, 9))
    
    # Select K=4 for optimal balance of inertia elbow and silhouette score
    df_final, cluster_profiles, cluster_eval = apply_kmeans_clustering(df_segmented, X_scaled, n_clusters=4)

    segments_file = processed_dir / "customer_segments.csv"
    df_final.to_csv(segments_file, index=False)
    logger.info(f"Saved final segmented & clustered dataset to: {segments_file}")

    # Step 7: Save EDA & Analytical Visualizations
    sns.set_theme(style="whitegrid", palette="muted")

    # Figure 1: Monthly Revenue Trend
    plt.figure(figsize=(10, 5))
    monthly_rev = df_feat.groupby("InvoiceMonthYear")["Revenue"].sum().reset_index()
    sns.lineplot(data=monthly_rev, x="InvoiceMonthYear", y="Revenue", marker="o", color="#2b5c8f", linewidth=2.5)
    plt.title("Monthly Revenue Trend (2010 - 2011)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Month-Year", fontsize=11)
    plt.ylabel("Total Revenue ($)", fontsize=11)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(figures_dir / "monthly_revenue.png", dpi=300)
    plt.close()

    # Figure 2: Top 10 Countries by Revenue (Excluding UK for visual balance if UK dominates, or showing overall top 10)
    plt.figure(figsize=(10, 5))
    country_rev = df_feat.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10).reset_index()
    sns.barplot(data=country_rev, x="Revenue", y="Country", palette="Blues_r")
    plt.title("Top 10 Countries by Revenue ($)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Total Revenue ($)", fontsize=11)
    plt.ylabel("Country", fontsize=11)
    plt.tight_layout()
    plt.savefig(figures_dir / "top_countries_revenue.png", dpi=300)
    plt.close()

    # Figure 3: RFM Metrics Distributions
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    sns.histplot(df_final["Recency"], bins=30, kde=True, ax=axes[0], color="#2b5c8f")
    axes[0].set_title("Recency Distribution (Days)")
    sns.histplot(df_final["Frequency"], bins=30, kde=True, ax=axes[1], color="#27ae60")
    axes[1].set_title("Frequency Distribution (Orders)")
    axes[1].set_yscale("log")
    sns.histplot(df_final["Monetary"], bins=30, kde=True, ax=axes[2], color="#e74c3c")
    axes[2].set_title("Monetary Distribution ($)")
    axes[2].set_yscale("log")
    plt.tight_layout()
    plt.savefig(figures_dir / "rfm_distributions.png", dpi=300)
    plt.close()

    # Figure 4: Customer Segment Distribution
    plt.figure(figsize=(10, 5))
    seg_counts = df_final["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]
    sns.barplot(data=seg_counts, x="Count", y="Segment", palette="viridis")
    plt.title("Customer Distribution by Business Segment", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Customers", fontsize=11)
    plt.ylabel("Segment", fontsize=11)
    plt.tight_layout()
    plt.savefig(figures_dir / "customer_segments_distribution.png", dpi=300)
    plt.close()

    # Figure 5: K-Means Evaluation (Elbow & Silhouette)
    fig, ax1 = plt.subplots(figsize=(8, 4))
    color = "tab:blue"
    ax1.set_xlabel("Number of Clusters (K)")
    ax1.set_ylabel("Inertia (Elbow)", color=color)
    ax1.plot(k_eval_df["K"], k_eval_df["Inertia"], marker="o", color=color, linewidth=2)
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Silhouette Score", color=color)
    ax2.plot(k_eval_df["K"], k_eval_df["Silhouette_Score"], marker="s", color=color, linewidth=2, linestyle="--")
    ax2.tick_params(axis="y", labelcolor=color)

    plt.title("K-Means Cluster Evaluation (Elbow Method & Silhouette Score)")
    plt.tight_layout()
    plt.savefig(figures_dir / "kmeans_elbow_silhouette.png", dpi=300)
    plt.close()

    # Collect Final Dataset Summary Metrics
    pipeline_summary = {
        "raw_rows": raw_stats["num_rows"],
        "raw_customers": raw_stats["unique_customers"],
        "raw_invoices": raw_stats["unique_invoices"],
        "raw_countries": raw_stats["unique_countries"],
        "cleaned_rows": cleaning_metrics["cleaned_rows"],
        "removed_rows": cleaning_metrics["total_removed"],
        "cancellations_removed": cleaning_metrics["cancellations_removed"],
        "missing_customer_id_removed": cleaning_metrics["missing_customer_id_removed"],
        "cleaned_unique_customers": int(df_final["CustomerID"].nunique()),
        "cleaned_unique_invoices": int(df_feat["InvoiceNo"].nunique()),
        "total_revenue": round(float(df_feat["Revenue"].sum()), 2),
        "avg_order_value": round(float(df_feat.groupby("InvoiceNo")["Revenue"].sum().mean()), 2),
        "avg_customer_revenue": round(float(df_final["Monetary"].mean()), 2),
        "snapshot_date": str(snapshot_date),
        "min_invoice_date": str(df_feat["InvoiceDate"].min()),
        "max_invoice_date": str(df_feat["InvoiceDate"].max()),
        "num_segments": int(df_final["Segment"].nunique()),
        "kmeans_silhouette_score": round(cluster_eval["silhouette_score"], 4),
        "k_clusters": cluster_eval["n_clusters"]
    }

    metrics_json_file = reports_dir / "pipeline_summary.json"
    with open(metrics_json_file, "w") as f:
        json.dump(pipeline_summary, f, indent=4)
    logger.info(f"Saved pipeline summary to: {metrics_json_file}")

    logger.info("==========================================")
    logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("==========================================")
    return pipeline_summary, df_final, df_feat, segment_summary, cluster_profiles

if __name__ == "__main__":
    run_pipeline()
