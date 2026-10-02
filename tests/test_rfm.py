"""
Unit tests for RFM calculation and scoring module.
"""

import pandas as pd
import pytest
from src.rfm_analysis import calculate_rfm, calculate_rfm_scores

@pytest.fixture
def sample_cleaned_data():
    return pd.DataFrame({
        "InvoiceNo": ["10001", "10002", "10003", "10004", "10005"],
        "StockCode": ["A", "B", "C", "D", "E"],
        "Quantity": [10, 5, 2, 20, 1],
        "UnitPrice": [2.0, 4.0, 10.0, 5.0, 50.0],
        "Revenue": [20.0, 20.0, 20.0, 100.0, 50.0],
        "InvoiceDate": pd.to_datetime([
            "2011-01-01 10:00:00",
            "2011-01-05 11:00:00",
            "2011-01-10 12:00:00",
            "2011-01-15 14:00:00",
            "2011-01-20 16:00:00"
        ]),
        "CustomerID": [101, 101, 102, 103, 104],
        "Country": ["UK", "UK", "UK", "UK", "UK"]
    })

def test_calculate_rfm(sample_cleaned_data):
    rfm_df, snapshot_date = calculate_rfm(sample_cleaned_data)
    assert len(rfm_df) == 4
    assert set(rfm_df.columns) == {"CustomerID", "Recency", "Frequency", "Monetary"}
    
    # Customer 101 has 2 invoices, total revenue 40.0
    cust101 = rfm_df[rfm_df["CustomerID"] == 101].iloc[0]
    assert cust101["Frequency"] == 2
    assert cust101["Monetary"] == 40.0

def test_calculate_rfm_scores_range(sample_cleaned_data):
    rfm_df, _ = calculate_rfm(sample_cleaned_data)
    rfm_scored = calculate_rfm_scores(rfm_df)
    
    for col in ["R_Score", "F_Score", "M_Score"]:
        assert rfm_scored[col].min() >= 1
        assert rfm_scored[col].max() <= 5
        
    assert (rfm_scored["RFM_Total_Score"] >= 3).all()
    assert (rfm_scored["RFM_Total_Score"] <= 15).all()
