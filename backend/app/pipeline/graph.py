"""LangGraph pipeline definition."""
from langgraph.graph import StateGraph, END
from .state import PipelineState
from .nodes import (
    load_data,
    profile_schema,
    check_quality,
    explain_issues,
    recommend_fixes,
    generate_report
)


def should_explain(state: PipelineState) -> str:
    """Conditional edge function: should we explain issues?"""
    issues = state.get("quality_issues", [])
    if issues:
        return "explain"
    return "generate_report"


def create_pipeline() -> StateGraph:
    """Create and compile the LangGraph pipeline."""
    # Create the graph
    workflow = StateGraph(PipelineState)
    
    # Add nodes
    workflow.add_node("load_data", load_data)
    workflow.add_node("profile_schema", profile_schema)
    workflow.add_node("check_quality", check_quality)
    workflow.add_node("explain_issues", explain_issues)
    workflow.add_node("recommend_fixes", recommend_fixes)
    workflow.add_node("generate_report", generate_report)
    
    # Set entry point
    workflow.set_entry_point("load_data")
    
    # Add edges
    workflow.add_edge("load_data", "profile_schema")
    workflow.add_edge("profile_schema", "check_quality")
    
    # Conditional edge: only explain if issues exist
    workflow.add_conditional_edges(
        "check_quality",
        should_explain,
        {
            "explain": "explain_issues",
            "generate_report": "generate_report"
        }
    )
    
    # If explaining, then recommend fixes, then generate report
    workflow.add_edge("explain_issues", "recommend_fixes")
    workflow.add_edge("recommend_fixes", "generate_report")
    
    # End after report generation
    workflow.add_edge("generate_report", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Create the pipeline instance
pipeline = create_pipeline()

