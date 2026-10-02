"""
Feature engineering module for creating transaction-level features.
"""

import pandas as pd
from src.utils import setup_logger

logger = setup_logger(__name__)

def add_transaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers transaction-level features for EDA and RFM analysis.
    
    Features created:
    - Revenue = Quantity * UnitPrice
    - InvoiceYear, InvoiceMonth, InvoiceDay, InvoiceHour
    - InvoiceMonthYear (YYYY-MM string)
    """
    df_feat = df.copy()
    
    # Calculate Revenue
    df_feat["Revenue"] = df_feat["Quantity"] * df_feat["UnitPrice"]
    
    # Sanity check: Revenue must be strictly positive for completed purchases
    invalid_rev_count = (df_feat["Revenue"] <= 0).sum()
    if invalid_rev_count > 0:
        logger.warning(f"Found {invalid_rev_count} rows with Revenue <= 0. Removing them.")
        df_feat = df_feat[df_feat["Revenue"] > 0]

    # Date component features
    df_feat["InvoiceDate"] = pd.to_datetime(df_feat["InvoiceDate"])
    df_feat["InvoiceYear"] = df_feat["InvoiceDate"].dt.year
    df_feat["InvoiceMonth"] = df_feat["InvoiceDate"].dt.month
    df_feat["InvoiceDay"] = df_feat["InvoiceDate"].dt.day
    df_feat["InvoiceHour"] = df_feat["InvoiceDate"].dt.hour
    df_feat["InvoiceMonthYear"] = df_feat["InvoiceDate"].dt.strftime("%Y-%m")

    logger.info("Successfully added Revenue and temporal date features.")
    return df_feat
