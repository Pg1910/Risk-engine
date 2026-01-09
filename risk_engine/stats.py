import pandas as pd
from collections import Counter
from typing import Any


def compute_summary(
    total_rows: int,
    flagged_rows: int,
    threshold: int,
    active_features: set[str]
) -> dict[str, Any]:
    """Generate summary statistics for the processing run."""
    return {
        "total_transactions": total_rows,
        "flagged_transactions": flagged_rows,
        "anomaly_rate": round(flagged_rows / total_rows, 6) if total_rows else 0,
        "threshold": threshold,
        "features_used": sorted(list(active_features))
    }


def risk_score_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate distribution of risk scores."""
    return (
        df["final_risk_score"]
        .value_counts()
        .sort_index()
        .reset_index()
        .rename(columns={"final_risk_score": "risk_score", "count": "count"})
    )

def reason_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate breakdown of anomaly reasons."""
    counter = Counter(
        reason
        for reasons in df["final_reasons"]
        for reason in (reasons if isinstance(reasons, list) else [])
    )
    return (
        pd.DataFrame(counter.items(), columns=["reason", "count"])
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )
