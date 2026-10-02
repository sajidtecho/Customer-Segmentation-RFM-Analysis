"""
K-Means Clustering module for unsupervised ML customer segmentation.
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from src.utils import setup_logger

logger = setup_logger(__name__)

def prepare_clustering_data(rfm_df: pd.DataFrame) -> Tuple[np.ndarray, StandardScaler, pd.DataFrame]:
    """
    Applies log transformation (log1p) to reduce right-skewness and standardizes RFM features.
    """
    rfm_log = pd.DataFrame()
    rfm_log["Recency"] = np.log1p(rfm_df["Recency"])
    rfm_log["Frequency"] = np.log1p(rfm_df["Frequency"])
    rfm_log["Monetary"] = np.log1p(rfm_df["Monetary"].clip(lower=0))

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(rfm_log)
    
    return X_scaled, scaler, rfm_log

def evaluate_kmeans_k(X_scaled: np.ndarray, k_range=range(2, 9)) -> pd.DataFrame:
    """
    Evaluates KMeans over a range of K using Inertia (Elbow) and Silhouette Scores.
    """
    results = []
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        inertia = kmeans.inertia_
        sil = silhouette_score(X_scaled, labels)
        results.append({"K": k, "Inertia": round(inertia, 2), "Silhouette_Score": round(sil, 4)})

    return pd.DataFrame(results)

def apply_kmeans_clustering(rfm_df: pd.DataFrame, X_scaled: np.ndarray, n_clusters: int = 4) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Fits KMeans model with chosen n_clusters and computes cluster profiles.
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    df_clustered = rfm_df.copy()
    df_clustered["Cluster"] = labels
    df_clustered["Cluster_Label"] = df_clustered["Cluster"].apply(lambda c: f"Cluster {c}")

    # Compute Cluster Profiles
    total_customers = len(df_clustered)
    total_revenue = df_clustered["Monetary"].sum()

    profiles = df_clustered.groupby("Cluster").agg(
        customer_count=("CustomerID", "count"),
        total_revenue=("Monetary", "sum"),
        avg_recency=("Recency", "mean"),
        avg_frequency=("Frequency", "mean"),
        avg_monetary=("Monetary", "mean")
    ).reset_index()

    profiles["customer_pct"] = (profiles["customer_count"] / total_customers * 100).round(2)
    profiles["revenue_pct"] = (profiles["total_revenue"] / total_revenue * 100).round(2)
    profiles["total_revenue"] = profiles["total_revenue"].round(2)
    profiles["avg_recency"] = profiles["avg_recency"].round(1)
    profiles["avg_frequency"] = profiles["avg_frequency"].round(2)
    profiles["avg_monetary"] = profiles["avg_monetary"].round(2)

    # Assign meaningful business labels based on cluster profiles
    def label_cluster(row):
        r, f, m = row["avg_recency"], row["avg_frequency"], row["avg_monetary"]
        if f > 8 and m > 3000:
            return "VIP High-Spenders"
        elif r < 60 and f >= 3:
            return "Active Frequent Buyers"
        elif r >= 150:
            return "Dormant / Lost"
        else:
            return "Occasional Low-Spenders"

    profiles["Business_Name"] = profiles.apply(label_cluster, axis=1)

    eval_summary = {
        "n_clusters": n_clusters,
        "inertia": float(kmeans.inertia_),
        "silhouette_score": float(silhouette_score(X_scaled, labels))
    }

    logger.info(f"Fitted KMeans with K={n_clusters}. Silhouette score: {eval_summary['silhouette_score']:.4f}")
    return df_clustered, profiles, eval_summary
