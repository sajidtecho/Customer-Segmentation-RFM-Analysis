"""
Unit tests for customer segmentation module.
"""

import pandas as pd
import pytest
from src.segmentation import segment_customers

@pytest.fixture
def sample_rfm_scored():
    return pd.DataFrame({
        "CustomerID": [1, 2, 3, 4, 5],
        "Recency": [5, 20, 100, 200, 300],
        "Frequency": [10, 4, 3, 2, 1],
        "Monetary": [5000.0, 1500.0, 400.0, 300.0, 50.0],
        "R_Score": [5, 4, 3, 2, 1],
        "F_Score": [5, 4, 3, 2, 1],
        "M_Score": [5, 4, 3, 2, 1],
        "RFM_Score": ["555", "444", "333", "222", "111"],
        "RFM_Total_Score": [15, 12, 9, 6, 3]
    })

def test_segment_customers_labels(sample_rfm_scored):
    df_segmented, summary = segment_customers(sample_rfm_scored)
    assert "Segment" in df_segmented.columns
    assert df_segmented["Segment"].isnull().sum() == 0
    assert len(summary) > 0

def test_segment_customers_non_negative_monetary(sample_rfm_scored):
    df_segmented, _ = segment_customers(sample_rfm_scored)
    assert (df_segmented["Monetary"] >= 0).all()
    assert (df_segmented["CustomerID"].notnull()).all()
