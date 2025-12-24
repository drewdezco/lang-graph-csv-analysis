"""Pydantic models for request/response schemas."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response model for file upload."""
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")
    job_id: Optional[str] = Field(None, description="Optional job identifier")


class SchemaProfile(BaseModel):
    """Schema profiling information."""
    columns: List[str] = Field(..., description="Column names")
    column_types: Dict[str, str] = Field(..., description="Data types for each column")
    null_counts: Dict[str, int] = Field(..., description="Null count per column")
    null_percentages: Dict[str, float] = Field(..., description="Null percentage per column")
    row_count: int = Field(..., description="Total number of rows")
    sample_values: Dict[str, List[Any]] = Field(..., description="Sample values per column")


class QualityIssue(BaseModel):
    """A detected data quality issue."""
    issue_type: str = Field(..., description="Type of issue (e.g., 'null_values', 'duplicates', 'outliers')")
    column: Optional[str] = Field(None, description="Column name if issue is column-specific")
    severity: str = Field(..., description="Severity level: 'low', 'medium', 'high'")
    description: str = Field(..., description="Description of the issue")
    affected_rows: Optional[int] = Field(None, description="Number of rows affected")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional issue details")


class IssueExplanation(BaseModel):
    """LLM-generated explanation for an issue."""
    issue_id: str = Field(..., description="Identifier for the issue")
    explanation: str = Field(..., description="Plain language explanation")


class FixRecommendation(BaseModel):
    """LLM-generated fix recommendation."""
    issue_id: str = Field(..., description="Identifier for the issue")
    recommendation: str = Field(..., description="Recommended fix")
    steps: Optional[List[str]] = Field(None, description="Step-by-step fix instructions")


class AnalysisReport(BaseModel):
    """Complete data quality analysis report."""
    schema_profile: SchemaProfile = Field(..., description="Schema profiling results")
    quality_issues: List[QualityIssue] = Field(default_factory=list, description="Detected quality issues")
    explanations: List[IssueExplanation] = Field(default_factory=list, description="Issue explanations")
    recommendations: List[FixRecommendation] = Field(default_factory=list, description="Fix recommendations")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")

