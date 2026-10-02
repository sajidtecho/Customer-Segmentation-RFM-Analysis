"""
RFM Analysis module for calculating Recency, Frequency, Monetary values and 1-5 Scores.
"""

from typing import Tuple
import pandas as pd
import numpy as np
from src.utils import setup_logger

logger = setup_logger(__name__)

def calculate_rfm(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Timestamp]:
    """
    Calculates customer-level Recency, Frequency, and Monetary metrics.

    Args:
        df: Cleaned transaction DataFrame with Revenue and InvoiceDate.

    Returns:
        Tuple[pd.DataFrame, pd.Timestamp]: RFM DataFrame and the snapshot reference date.
    """
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    logger.info(f"Dynamic snapshot reference date: {snapshot_date}")

    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum")
    ).reset_index()

    # Convert Recency and Frequency to integers
    rfm["Recency"] = rfm["Recency"].astype(int)
    rfm["Frequency"] = rfm["Frequency"].astype(int)
    rfm["Monetary"] = rfm["Monetary"].round(2)

    logger.info(f"Calculated RFM metrics for {len(rfm)} unique customers.")
    return rfm, snapshot_date

def calculate_rfm_scores(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes 1-5 RFM scores using robust quantile binning.
    
    Handles duplicate quantile boundaries safely using rank(method='first') before qcut.
    - Recency: lower recency = higher score (5 to 1)
    - Frequency: higher frequency = higher score (1 to 5)
    - Monetary: higher monetary = higher score (1 to 5)
    """
    rfm_scored = rfm_df.copy()

    # Recency scoring (Reverse: 5 = most recent, 1 = least recent)
    r_ranked = rfm_scored["Recency"].rank(method="first", ascending=True)
    rfm_scored["R_Score"] = pd.qcut(r_ranked, q=5, labels=[5, 4, 3, 2, 1]).astype(int)

    # Frequency scoring (1 = lowest frequency, 5 = highest frequency)
    f_ranked = rfm_scored["Frequency"].rank(method="first", ascending=True)
    rfm_scored["F_Score"] = pd.qcut(f_ranked, q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Monetary scoring (1 = lowest monetary, 5 = highest monetary)
    m_ranked = rfm_scored["Monetary"].rank(method="first", ascending=True)
    rfm_scored["M_Score"] = pd.qcut(m_ranked, q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Concatenate scores into a string and total score
    rfm_scored["RFM_Score"] = (
        rfm_scored["R_Score"].astype(str) +
        rfm_scored["F_Score"].astype(str) +
        rfm_scored["M_Score"].astype(str)
    )
    rfm_scored["RFM_Total_Score"] = rfm_scored["R_Score"] + rfm_scored["F_Score"] + rfm_scored["M_Score"]

    logger.info("Successfully computed R_Score, F_Score, M_Score, RFM_Score, and RFM_Total_Score.")
    return rfm_scored
