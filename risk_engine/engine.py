"""Core engine for processing transaction data and detecting anomalies."""

import json
import os
from typing import Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

import pandas as pd

from risk_engine.io import (
    append_csv,
    append_parquet,
    ensure_dir,
    read_csv_in_chunks,
)
from risk_engine.rules import process_transactions
from risk_engine.stats import (
    compute_summary,
    reason_breakdown,
    risk_score_distribution,
)
from risk_engine.utils import setup_logger

logger = setup_logger()


def _process_chunk(args: tuple) -> tuple:
    """
    Process a single chunk - designed for parallel execution.
    
    Args:
        args: Tuple of (chunk_idx, chunk_data, simulation, threshold)
    
    Returns:
        Tuple of (chunk_idx, total_rows, flagged_df, available_features, used_threshold)
    """
    chunk_idx, chunk, simulation, threshold = args
    
    available_features = set(chunk.columns)
    
    processed = process_transactions(
        chunk,
        simulation_mode=simulation,
        available_features=available_features,
        threshold_override=threshold,
    )
    
    used_threshold = processed.attrs.get("threshold", threshold)
    flagged = processed[processed["final_is_anomalous"]].copy()
    
    return (chunk_idx, len(chunk), flagged, available_features, used_threshold)


def run_engine(
    input_file: str,
    output_dir: str,
    threshold: Optional[int] = None,
    simulation: bool = False,
    chunk_size: int = 500_000,
    quiet: bool = False,
    workers: Optional[int] = None,
) -> dict:
    """
    Run the anomaly detection engine on a transaction dataset.

    Args:
        input_file: Path to input CSV file
        output_dir: Directory for output files
        threshold: Override risk score threshold (None = auto-calculate)
        simulation: Enable velocity simulation mode
        chunk_size: Rows per processing chunk
        quiet: Suppress progress output
        workers: Number of parallel workers (None = auto-detect CPU count)

    Returns:
        Summary dictionary with processing results
    """
    ensure_dir(output_dir)

    flagged_csv = os.path.join(output_dir, "flagged_transactions.csv")
    flagged_parquet = os.path.join(output_dir, "flagged_transactions.parquet")

    # Clean up existing output files
    for f in [flagged_csv, flagged_parquet]:
        if os.path.exists(f):
            os.remove(f)

    # Determine number of workers
    if workers is None:
        workers = multiprocessing.cpu_count()
    workers = max(1, min(workers, multiprocessing.cpu_count()))
    
    if not quiet:
        print(f"[INFO] Using {workers} CPU cores for parallel processing")

    # Read all chunks first (needed for parallel processing)
    chunks = list(read_csv_in_chunks(input_file, chunk_size))
    total_chunks = len(chunks)
    
    if not quiet:
        print(f"[INFO] Loaded {total_chunks} chunk(s), starting parallel processing...")

    total_rows = 0
    total_flagged = 0
    all_flagged_chunks = []
    available_features: set = set()
    used_threshold = threshold

    if workers == 1 or total_chunks == 1:
        # Sequential processing (single core or single chunk)
        for chunk_idx, chunk in enumerate(chunks):
            if not quiet:
                print(f"[INFO] Processing chunk {chunk_idx + 1}/{total_chunks} ({len(chunk):,} rows)")

            total_rows += len(chunk)
            available_features = set(chunk.columns)

            processed = process_transactions(
                chunk,
                simulation_mode=simulation,
                available_features=available_features,
                threshold_override=threshold,
            )

            if used_threshold is None:
                used_threshold = processed.attrs.get("threshold", threshold)

            flagged = processed[processed["final_is_anomalous"]]
            total_flagged += len(flagged)

            if not flagged.empty:
                export_cols = _get_export_columns(flagged)
                flagged_export = flagged[export_cols].copy()
                
                if "final_reasons" in flagged_export.columns:
                    flagged_export["final_reasons"] = flagged_export["final_reasons"].apply(
                        lambda x: "; ".join(x) if isinstance(x, list) else str(x)
                    )

                append_csv(flagged_export, flagged_csv)
                append_parquet(flagged_export, flagged_parquet)
                all_flagged_chunks.append(flagged)
    else:
        # Parallel processing with multiple cores
        chunk_args = [
            (idx, chunk, simulation, threshold) 
            for idx, chunk in enumerate(chunks)
        ]
        
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_process_chunk, args): args[0] for args in chunk_args}
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                try:
                    chunk_idx, rows, flagged, features, thresh = future.result()
                    
                    total_rows += rows
                    total_flagged += len(flagged)
                    available_features = features
                    
                    if used_threshold is None:
                        used_threshold = thresh
                    
                    if not flagged.empty:
                        all_flagged_chunks.append(flagged)
                    
                    if not quiet:
                        print(f"[INFO] Completed chunk {completed}/{total_chunks} ({rows:,} rows, {len(flagged):,} flagged)")
                        
                except Exception as e:
                    if not quiet:
                        print(f"[ERROR] Chunk processing failed: {e}")

        # Write all flagged data after parallel processing completes
        if all_flagged_chunks:
            all_flagged_combined = pd.concat(all_flagged_chunks, ignore_index=True)
            export_cols = _get_export_columns(all_flagged_combined)
            flagged_export = all_flagged_combined[export_cols].copy()
            
            if "final_reasons" in flagged_export.columns:
                flagged_export["final_reasons"] = flagged_export["final_reasons"].apply(
                    lambda x: "; ".join(x) if isinstance(x, list) else str(x)
                )
            
            append_csv(flagged_export, flagged_csv)
            append_parquet(flagged_export, flagged_parquet)

    # Aggregate stats only on flagged data
    if all_flagged_chunks:
        all_flagged = pd.concat(all_flagged_chunks, ignore_index=True)
    else:
        all_flagged = pd.DataFrame()

    # Stats outputs
    if not all_flagged.empty:
        risk_score_distribution(all_flagged).to_csv(
            os.path.join(output_dir, "stats_risk_scores.csv"),
            index=False
        )

        reason_breakdown(all_flagged).to_csv(
            os.path.join(output_dir, "stats_reasons.csv"),
            index=False
        )

    summary = compute_summary(
        total_rows=total_rows,
        flagged_rows=total_flagged,
        threshold=used_threshold or 0,
        active_features=available_features
    )

    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    if not quiet:
        print("[DONE] Processing complete")
        print(json.dumps(summary, indent=2))

    return summary


def _get_export_columns(df: pd.DataFrame) -> list[str]:
    """Get columns to include in export, excluding internal columns."""
    # Core columns to always include if present
    priority_cols = [
        "transaction_id",
        "sender_account",
        "timestamp",
        "amount",
        "location",
        "device_hash",
        "ip_address",
        "hour",
        "final_risk_score",
        "final_reasons",
        "final_is_anomalous",
    ]
    
    # Include priority columns that exist
    export_cols = [c for c in priority_cols if c in df.columns]
    
    # Add any risk columns
    risk_cols = [c for c in df.columns if c.startswith("risk_") and c not in export_cols]
    export_cols.extend(sorted(risk_cols))
    
    return export_cols
