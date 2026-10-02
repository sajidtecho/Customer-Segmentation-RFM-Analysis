"""
Unit tests for data cleaning module.
"""

import pandas as pd
import pytest
from src.data_cleaning import clean_transactions
from src.feature_engineering import add_transaction_features

@pytest.fixture
def sample_raw_data():
    return pd.DataFrame({
        "InvoiceNo": ["536365", "C536366", "536367", "536368", "536368"],
        "StockCode": ["85123A", "71053", "84406B", "84029G", "84029G"],
        "Description": ["WHITE HANGING HEART", "WHITE METAL LANTERN", "CREAM CUPID HEARTS", "KNITTED UNION FLAG", "KNITTED UNION FLAG"],
        "Quantity": [6, -1, 8, 6, 6],
        "InvoiceDate": ["2010-12-01 08:26:00", "2010-12-01 08:28:00", "2010-12-01 08:34:00", "2010-12-01 08:34:00", "2010-12-01 08:34:00"],
        "UnitPrice": [2.55, 3.39, 2.75, 3.39, 3.39],
        "CustomerID": [17850.0, 17850.0, 13047.0, None, 13047.0],
        "Country": ["United Kingdom", "United Kingdom", "United Kingdom", "United Kingdom", "United Kingdom"]
    })

def test_clean_transactions_removes_cancellations(sample_raw_data):
    cleaned_df, metrics = clean_transactions(sample_raw_data)
    assert metrics["cancellations_removed"] == 1
    assert not any(cleaned_df["InvoiceNo"].str.startswith("C"))

def test_clean_transactions_removes_missing_customer_id(sample_raw_data):
    cleaned_df, metrics = clean_transactions(sample_raw_data)
    assert cleaned_df["CustomerID"].isnull().sum() == 0

def test_add_transaction_features_revenue(sample_raw_data):
    cleaned_df, _ = clean_transactions(sample_raw_data)
    feat_df = add_transaction_features(cleaned_df)
    assert "Revenue" in feat_df.columns
    assert (feat_df["Revenue"] == feat_df["Quantity"] * feat_df["UnitPrice"]).all()
    assert (feat_df["Revenue"] > 0).all()
