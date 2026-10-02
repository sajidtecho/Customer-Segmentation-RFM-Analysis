"""
Data loader module for reading and inspecting raw transaction data.
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd
from src.utils import get_project_root, setup_logger

logger = setup_logger(__name__)

def find_data_file(custom_path: str = None) -> Path:
    """Locate the raw dataset file (Excel or CSV)."""
    if custom_path:
        path = Path(custom_path)
        if path.exists():
            return path

    root = get_project_root()
    possible_paths = [
        root / "data" / "raw" / "Online Retail.xlsx",
        root / "data" / "Online Retail.xlsx",
        root / "data" / "raw" / "Online_Retail.xlsx",
        root / "data" / "raw" / "online_retail.csv"
    ]
    for p in possible_paths:
        if p.exists():
            return p

    raise FileNotFoundError(
        "Raw dataset not found! Please ensure 'Online Retail.xlsx' is placed at 'data/raw/Online Retail.xlsx' or 'data/Online Retail.xlsx'."
    )

def load_raw_data(data_path: str = None) -> pd.DataFrame:
    """Load raw transactions dataset."""
    file_path = find_data_file(data_path)
    logger.info(f"Loading raw dataset from: {file_path}")
    
    if file_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path, encoding="ISO-8859-1")
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    logger.info(f"Successfully loaded raw dataset with shape: {df.shape}")
    return df

def inspect_raw_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive raw dataset statistics."""
    stats = {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "column_names": list(df.columns),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_invoices": int(df["InvoiceNo"].nunique()) if "InvoiceNo" in df else 0,
        "unique_products": int(df["StockCode"].nunique()) if "StockCode" in df else 0,
        "unique_customers": int(df["CustomerID"].dropna().nunique()) if "CustomerID" in df else 0,
        "unique_countries": int(df["Country"].nunique()) if "Country" in df else 0,
        "min_date": str(df["InvoiceDate"].min()) if "InvoiceDate" in df else None,
        "max_date": str(df["InvoiceDate"].max()) if "InvoiceDate" in df else None,
    }
    return stats
