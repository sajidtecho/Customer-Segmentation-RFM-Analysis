"""
Customer segmentation module defining transparent, rule-based business segments.
"""

from typing import Tuple
import pandas as pd
from src.utils import setup_logger

logger = setup_logger(__name__)

def assign_segment(row: pd.Series) -> str:
    """
    Rule-based mapping from RFM scores to business segments.
    """
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]

    # Champions: Bought recently, buy often, and spend the most
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    
    # Loyal Customers: Buy regularly, responsive to promotions
    if r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"

    # Big Spenders: High monetary contribution
    if m >= 4:
        return "Big Spenders"

    # Potential Loyalists: Recent buyers with moderate frequency
    if r >= 4 and f in [2, 3]:
        return "Potential Loyalists"

    # New Customers: Bought recently, low frequency (1 order)
    if r >= 4 and f == 1:
        return "New Customers"

    # Need Attention: Above average recency, frequency, and monetary value
    if r in [2, 3] and f in [2, 3]:
        return "Need Attention"

    # At Risk: Spent good money and bought often, but haven't purchased in a long time
    if r <= 2 and (f >= 3 or m >= 3):
        return "At Risk"

    # Lost Customers: Lowest recency, frequency, and monetary scores
    if r == 1 and f <= 2 and m <= 2:
        return "Lost Customers"

    # Fallback category for any remaining boundary combinations
    return "Hibernating / Low Value"

def segment_customers(rfm_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Assigns business segments to customers and computes segment summary statistics.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Segmented customer DataFrame and Segment Summary DataFrame.
    """
    df_segmented = rfm_df.copy()
    df_segmented["Segment"] = df_segmented.apply(assign_segment, axis=1)

    # Compute Segment Aggregation Metrics
    total_customers = len(df_segmented)
    total_revenue = df_segmented["Monetary"].sum()

    summary = df_segmented.groupby("Segment").agg(
        customer_count=("CustomerID", "count"),
        total_revenue=("Monetary", "sum"),
        avg_recency=("Recency", "mean"),
        avg_frequency=("Frequency", "mean"),
        avg_monetary=("Monetary", "mean")
    ).reset_index()

    summary["customer_pct"] = (summary["customer_count"] / total_customers * 100).round(2)
    summary["revenue_pct"] = (summary["total_revenue"] / total_revenue * 100).round(2)

    # Round numeric summary columns
    summary["total_revenue"] = summary["total_revenue"].round(2)
    summary["avg_recency"] = summary["avg_recency"].round(1)
    summary["avg_frequency"] = summary["avg_frequency"].round(2)
    summary["avg_monetary"] = summary["avg_monetary"].round(2)

    # Sort summary by revenue descending
    summary = summary.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)

    logger.info(f"Successfully segmented {total_customers} customers into {summary['Segment'].nunique()} segments.")
    return df_segmented, summary
