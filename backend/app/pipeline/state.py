"""LangGraph state schema for the data quality pipeline."""
from typing import TypedDict, Dict, List, Any, Optional
import pandas as pd


class PipelineState(TypedDict):
    """State schema for the LangGraph pipeline."""
    csv_data: Optional[pd.DataFrame]  # Loaded CSV data
    schema_profile: Optional[Dict[str, Any]]  # Schema profiling results
    quality_issues: List[Dict[str, Any]]  # Detected quality issues
    explanations: Dict[str, str]  # Issue explanations (issue_id -> explanation)
    recommendations: Dict[str, str]  # Fix recommendations (issue_id -> recommendation)
    report: Optional[Dict[str, Any]]  # Final structured report

