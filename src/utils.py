"""
Utility functions for file paths, formatting, directory management, and logging.
"""

from pathlib import Path
import logging

def get_project_root() -> Path:
    """Return the root directory of the project."""
    return Path(__file__).resolve().parent.parent

def ensure_directories():
    """Ensure all required project output directories exist."""
    root = get_project_root()
    dirs = [
        root / "data" / "raw",
        root / "data" / "processed",
        root / "reports" / "figures",
        root / "dashboard",
        root / "sql",
        root / "tests"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str = "customer_segmentation") -> logging.Logger:
    """Setup clean console logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def format_currency(value: float) -> str:
    """Format float value to USD currency format."""
    return f"${value:,.2f}"
