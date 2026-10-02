"""
Data cleaning module enforcing rigorous filtering and data integrity checks.
"""

from typing import Tuple, Dict, Any
import pandas as pd
from src.utils import setup_logger

logger = setup_logger(__name__)

def clean_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes a step-by-step cleaning pipeline on raw transaction data.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Cleaned DataFrame and detailed cleaning metrics dictionary.
    """
    metrics = {}
    initial_rows = len(df)
    metrics["initial_rows"] = initial_rows
    logger.info(f"Starting data cleaning pipeline. Initial row count: {initial_rows}")

    current_df = df.copy()

    # Step 1: Remove duplicate rows
    duplicate_rows = int(current_df.duplicated().sum())
    metrics["duplicates_removed"] = duplicate_rows
    current_df = current_df.drop_duplicates()
    logger.info(f"Removed {duplicate_rows} duplicate rows.")

    # Step 2: Handle missing CustomerID
    missing_customer_id = int(current_df["CustomerID"].isnull().sum())
    metrics["missing_customer_id_removed"] = missing_customer_id
    current_df = current_df.dropna(subset=["CustomerID"])
    logger.info(f"Removed {missing_customer_id} rows with missing CustomerID.")

    # Step 3: Handle missing Description
    missing_description = int(current_df["Description"].isnull().sum())
    metrics["missing_description_removed"] = missing_description
    current_df = current_df.dropna(subset=["Description"])
    logger.info(f"Removed {missing_description} rows with missing Description.")

    # Convert CustomerID to integer format (e.g. 17850 instead of 17850.0)
    current_df["CustomerID"] = current_df["CustomerID"].astype(int)

    # Step 4: Separate cancelled transactions (InvoiceNo starts with 'C')
    current_df["InvoiceNo"] = current_df["InvoiceNo"].astype(str)
    cancellations_mask = current_df["InvoiceNo"].str.startswith("C")
    cancellations_count = int(cancellations_mask.sum())
    metrics["cancellations_removed"] = cancellations_count
    current_df = current_df[~cancellations_mask]
    logger.info(f"Removed {cancellations_count} cancelled transactions (InvoiceNo starting with 'C').")

    # Step 5: Filter out non-positive quantities (Quantity <= 0)
    negative_quantity_mask = current_df["Quantity"] <= 0
    negative_quantity_count = int(negative_quantity_mask.sum())
    metrics["negative_or_zero_quantity_removed"] = negative_quantity_count
    current_df = current_df[~negative_quantity_mask]
    logger.info(f"Removed {negative_quantity_count} rows with Quantity <= 0.")

    # Step 6: Filter out non-positive unit prices (UnitPrice <= 0)
    invalid_price_mask = current_df["UnitPrice"] <= 0
    invalid_price_count = int(invalid_price_mask.sum())
    metrics["invalid_or_zero_price_removed"] = invalid_price_count
    current_df = current_df[~invalid_price_mask]
    logger.info(f"Removed {invalid_price_count} rows with UnitPrice <= 0.")

    # Convert InvoiceDate to datetime if not already
    current_df["InvoiceDate"] = pd.to_datetime(current_df["InvoiceDate"])

    cleaned_rows = len(current_df)
    total_removed = initial_rows - cleaned_rows
    metrics["cleaned_rows"] = cleaned_rows
    metrics["total_removed"] = total_removed
    metrics["retention_rate_pct"] = round((cleaned_rows / initial_rows) * 100, 2)

    logger.info(f"Cleaning complete. Remaining rows: {cleaned_rows} ({metrics['retention_rate_pct']}% retained).")
    return current_df, metrics
