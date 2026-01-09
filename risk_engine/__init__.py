"""Risk Engine - Explainable Transaction Anomaly Detection.

A secure, offline, explainable transaction anomaly detection engine
designed for banking environments.
"""

__version__ = "1.0.0"

# Direct imports
from risk_engine.engine import run_engine
from risk_engine.rules import process_transactions
from risk_engine.io import read_csv_in_chunks, append_csv, append_parquet
from risk_engine.stats import compute_summary, risk_score_distribution, reason_breakdown

__all__ = [
    "__version__",
    "run_engine",
    "process_transactions",
    "read_csv_in_chunks",
    "append_csv",
    "append_parquet",
    "compute_summary",
    "risk_score_distribution",
    "reason_breakdown",
]