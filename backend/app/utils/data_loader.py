"""Utilities for loading and processing CSV data."""
import pandas as pd
from typing import Optional
import io


def load_csv_from_bytes(file_bytes: bytes, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Load CSV data from bytes into a pandas DataFrame.
    
    Args:
        file_bytes: CSV file content as bytes
        encoding: File encoding (default: utf-8)
        
    Returns:
        pandas DataFrame with loaded data
    """
    try:
        # Try UTF-8 first
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")
    
    return df


def validate_csv(df: pd.DataFrame) -> tuple[bool, Optional[str]]:
    """
    Validate that the DataFrame is not empty and has valid structure.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df.empty:
        return False, "CSV file is empty"
    
    if df.shape[1] == 0:
        return False, "CSV file has no columns"
    
    return True, None

