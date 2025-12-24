"""FastAPI application with CSV upload and data quality analysis."""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables - look for .env in backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

from .models import UploadResponse, AnalysisReport
from .pipeline.graph import pipeline
from .pipeline.state import PipelineState
from .utils.data_loader import load_csv_from_bytes, validate_csv

app = FastAPI(
    title="CSV Data Quality Analysis API",
    description="API for analyzing CSV data quality using LangGraph",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and Create React App defaults
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CSV Data Quality Analysis API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file and run data quality analysis.
    
    Returns a structured report with schema profiling, quality issues,
    explanations, and recommendations.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Read file content
        file_bytes = await file.read()
        
        # Load CSV into DataFrame
        df = load_csv_from_bytes(file_bytes)
        
        # Validate CSV
        is_valid, error_message = validate_csv(df)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Initialize pipeline state
        initial_state: PipelineState = {
            "csv_data": df,
            "schema_profile": None,
            "quality_issues": [],
            "explanations": {},
            "recommendations": {},
            "report": None
        }
        
        # Run the pipeline
        try:
            final_state = pipeline.invoke(initial_state)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline execution failed: {str(e)}"
            )
        
        # Extract report from final state
        report = final_state.get("report")
        if report is None:
            raise HTTPException(
                status_code=500,
                detail="Pipeline did not generate a report"
            )
        
        # Return the report as JSON
        return JSONResponse(content=report)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

