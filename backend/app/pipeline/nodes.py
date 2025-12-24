"""LangGraph pipeline nodes for data quality analysis."""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from pathlib import Path
from dotenv import load_dotenv
from .state import PipelineState

# Load environment variables - look for .env in backend directory
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Lazy LLM initialization - only create when needed
_llm_instance = None

def get_llm():
    """Get or create the LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment variables."
            )
        _llm_instance = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            api_key=api_key,
            timeout=30.0,  # 30 second timeout
            max_retries=2
        )
    return _llm_instance


def load_data(state: PipelineState) -> PipelineState:
    """
    Load CSV data into the state.
    Note: CSV data should already be loaded before this node is called.
    """
    # This node is a pass-through as data is loaded in the API endpoint
    # But we can add validation here
    if state.get("csv_data") is None:
        raise ValueError("CSV data not found in state")
    
    return state


def profile_schema(state: PipelineState) -> PipelineState:
    """Profile the schema of the CSV data."""
    df: pd.DataFrame = state["csv_data"]
    
    # Basic schema information
    columns = df.columns.tolist()
    column_types = {col: str(df[col].dtype) for col in columns}
    
    # Null counts and percentages
    null_counts = df.isnull().sum().to_dict()
    null_percentages = {
        col: (null_counts[col] / len(df)) * 100 
        for col in columns
    }
    
    # Sample values (first 5 non-null values per column)
    sample_values = {}
    for col in columns:
        non_null_values = df[col].dropna().head(5).tolist()
        sample_values[col] = non_null_values
    
    schema_profile = {
        "columns": columns,
        "column_types": column_types,
        "null_counts": null_counts,
        "null_percentages": null_percentages,
        "row_count": len(df),
        "sample_values": sample_values
    }
    
    state["schema_profile"] = schema_profile
    return state


def check_quality(state: PipelineState) -> PipelineState:
    """Check data quality and detect issues."""
    df: pd.DataFrame = state["csv_data"]
    issues: List[Dict[str, Any]] = []
    
    # Check for null values
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        
        if null_pct > 0:
            severity = "high" if null_pct > 50 else "medium" if null_pct > 20 else "low"
            issues.append({
                "issue_id": f"null_values_{col}",
                "issue_type": "null_values",
                "column": col,
                "severity": severity,
                "description": f"Column '{col}' has {null_count} null values ({null_pct:.2f}%)",
                "affected_rows": int(null_count),
                "details": {
                    "null_count": int(null_count),
                    "null_percentage": round(null_pct, 2)
                }
            })
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        dup_pct = (duplicate_count / len(df)) * 100
        severity = "high" if dup_pct > 10 else "medium" if dup_pct > 5 else "low"
        issues.append({
            "issue_id": "duplicate_rows",
            "issue_type": "duplicates",
            "column": None,
            "severity": severity,
            "description": f"Found {duplicate_count} duplicate rows ({dup_pct:.2f}%)",
            "affected_rows": int(duplicate_count),
            "details": {
                "duplicate_count": int(duplicate_count),
                "duplicate_percentage": round(dup_pct, 2)
            }
        })
    
    # Check for type inconsistencies (numeric columns with non-numeric values)
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to detect if column should be numeric
            non_null = df[col].dropna()
            if len(non_null) > 0:
                # Check if values look numeric but aren't parsed as such
                numeric_count = 0
                for val in non_null.head(100):  # Sample check
                    try:
                        float(str(val).replace(',', '').replace('$', '').strip())
                        numeric_count += 1
                    except (ValueError, AttributeError):
                        pass
                
                if numeric_count > len(non_null.head(100)) * 0.8 and len(non_null) > 10:
                    issues.append({
                        "issue_id": f"type_mismatch_{col}",
                        "issue_type": "type_mismatch",
                        "column": col,
                        "severity": "medium",
                        "description": f"Column '{col}' appears to contain numeric data but is stored as text",
                        "affected_rows": len(non_null),
                        "details": {
                            "detected_type": "numeric",
                            "actual_type": "object"
                        }
                    })
    
    # Check for empty columns (both null and empty strings)
    for col in df.columns:
        # Check if column is all null
        is_all_null = df[col].isnull().all()
        
        # Check if column is all empty strings
        # Convert to string, strip whitespace, and check if all are empty
        str_values = df[col].astype(str).str.strip()
        is_all_empty_string = (str_values == '').all()
        
        if is_all_null or is_all_empty_string:
            issues.append({
                "issue_id": f"empty_column_{col}",
                "issue_type": "empty_column",
                "column": col,
                "severity": "high",
                "description": f"Column '{col}' is completely empty",
                "affected_rows": len(df),
                "details": {}
            })
    
    state["quality_issues"] = issues
    return state


def explain_issues(state: PipelineState) -> PipelineState:
    """Use LLM to explain detected issues in plain language."""
    issues = state.get("quality_issues", [])
    
    if not issues:
        state["explanations"] = {}
        return state
    
    explanations = {}
    
    # Create prompt for explaining issues
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a data quality expert. Explain data quality issues in clear, plain language that non-technical users can understand. Keep explanations concise (1-2 sentences maximum)."),
        ("human", "Explain this data quality issue:\n\nIssue Type: {issue_type}\nColumn: {column}\nDescription: {description}\n\nProvide a brief, clear explanation (1-2 sentences) of what this issue means and why it matters.")
    ])
    
    llm = get_llm()
    chain = prompt_template | llm | StrOutputParser()
    
    for issue in issues:
        try:
            explanation = chain.invoke({
                "issue_type": issue.get("issue_type", "unknown"),
                "column": issue.get("column", "N/A"),
                "description": issue.get("description", "")
            })
            explanations[issue["issue_id"]] = explanation
        except Exception as e:
            # Fallback explanation if LLM fails (timeout, API error, etc.)
            print(f"LLM call failed for issue {issue.get('issue_id')}: {str(e)}")
            explanations[issue["issue_id"]] = f"This issue indicates a potential data quality problem: {issue.get('description', 'Unknown issue')}"
    
    state["explanations"] = explanations
    return state


def recommend_fixes(state: PipelineState) -> PipelineState:
    """Use LLM to recommend fixes for detected issues."""
    issues = state.get("quality_issues", [])
    schema_profile = state.get("schema_profile", {})
    
    if not issues:
        state["recommendations"] = {}
        return state
    
    recommendations = {}
    
    # Create prompt for recommending fixes
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a data quality expert. Provide concise, actionable recommendations for fixing data quality issues. Keep responses brief (2-4 sentences maximum). Focus on the most important action steps."),
        ("human", "Issue Details:\nType: {issue_type}\nColumn: {column}\nDescription: {description}\nAffected Rows: {affected_rows}\n\nSchema Context:\nColumn Type: {column_type}\nNull Percentage: {null_pct}%\n\nProvide a concise recommendation (2-4 sentences) for fixing this issue. Be brief and actionable.")
    ])
    
    llm = get_llm()
    chain = prompt_template | llm | StrOutputParser()
    
    for issue in issues:
        try:
            col = issue.get("column", "N/A")
            col_type = schema_profile.get("column_types", {}).get(col, "unknown") if col != "N/A" else "N/A"
            null_pct = schema_profile.get("null_percentages", {}).get(col, 0) if col != "N/A" else 0
            
            recommendation = chain.invoke({
                "issue_type": issue.get("issue_type", "unknown"),
                "column": col,
                "description": issue.get("description", ""),
                "affected_rows": issue.get("affected_rows", 0),
                "column_type": col_type,
                "null_pct": round(null_pct, 2)
            })
            recommendations[issue["issue_id"]] = recommendation
        except Exception as e:
            # Fallback recommendation if LLM fails
            recommendations[issue["issue_id"]] = f"Review and clean the data for: {issue.get('description', 'Unknown issue')}"
    
    state["recommendations"] = recommendations
    return state


def generate_report(state: PipelineState) -> PipelineState:
    """Generate the final structured report."""
    schema_profile = state.get("schema_profile", {})
    issues = state.get("quality_issues", [])
    explanations = state.get("explanations", {})
    recommendations = state.get("recommendations", {})
    
    # Build explanations list
    explanations_list = [
        {"issue_id": issue_id, "explanation": explanation}
        for issue_id, explanation in explanations.items()
    ]
    
    # Build recommendations list
    recommendations_list = [
        {"issue_id": issue_id, "recommendation": recommendation}
        for issue_id, recommendation in recommendations.items()
    ]
    
    # Create summary
    summary = {
        "total_rows": schema_profile.get("row_count", 0),
        "total_columns": len(schema_profile.get("columns", [])),
        "total_issues": len(issues),
        "issues_by_severity": {
            "high": len([i for i in issues if i.get("severity") == "high"]),
            "medium": len([i for i in issues if i.get("severity") == "medium"]),
            "low": len([i for i in issues if i.get("severity") == "low"])
        },
        "issues_by_type": {}
    }
    
    # Count issues by type
    for issue in issues:
        issue_type = issue.get("issue_type", "unknown")
        summary["issues_by_type"][issue_type] = summary["issues_by_type"].get(issue_type, 0) + 1
    
    report = {
        "schema_profile": schema_profile,
        "quality_issues": issues,
        "explanations": explanations_list,
        "recommendations": recommendations_list,
        "summary": summary
    }
    
    state["report"] = report
    return state

