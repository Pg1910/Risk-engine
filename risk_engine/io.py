"""I/O utilities for reading and writing data files."""

import os
from typing import Iterator

import pandas as pd


def read_csv_in_chunks(path: str, chunk_size: int) -> Iterator[pd.DataFrame]:
    """
    Read a CSV file in chunks for memory-efficient processing.
    
    Args:
        path: Path to the CSV file
        chunk_size: Number of rows per chunk
        
    Yields:
        DataFrame chunks
    """
    return pd.read_csv(
        path,
        chunksize=chunk_size,
        low_memory=False
    )


def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def append_csv(df: pd.DataFrame, path: str) -> None:
    """Append DataFrame to CSV file, creating header only if file is new."""
    header = not os.path.exists(path)
    df.to_csv(path, mode="a", index=False, header=header)


def append_parquet(df: pd.DataFrame, path: str) -> None:
    """
    Append DataFrame to Parquet file.
    
    Note: This reads and rewrites the entire file, which is not ideal
    for very large files but ensures compatibility.
    """
    if not os.path.exists(path):
        df.to_parquet(path, index=False, engine="pyarrow")
    else:
        existing = pd.read_parquet(path)
        pd.concat([existing, df], ignore_index=True).to_parquet(
            path, index=False, engine="pyarrow"
        )
