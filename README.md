# CSV Data Quality Analysis Service

A FastAPI service with LangGraph pipeline for analyzing CSV data quality, detecting issues, and providing AI-powered explanations and recommendations. Includes a React frontend for easy file upload and results visualization.

## Features

- **CSV Upload**: REST API endpoint for uploading CSV files
- **Schema Profiling**: Automatic analysis of column types, null counts, and sample values
- **Quality Checks**: Detection of data quality issues (nulls, duplicates, type mismatches, etc.)
- **AI Explanations**: LLM-powered explanations of detected issues in plain language
- **Fix Recommendations**: AI-generated recommendations for resolving data quality issues
- **Structured Reports**: JSON responses with comprehensive analysis results
- **React Frontend**: Modern UI for uploading files and viewing results

## Architecture

- **Backend**: FastAPI with LangGraph pipeline orchestration
- **LLM Integration**: LangChain with OpenAI for explanations and recommendations
- **Frontend**: React with Vite for fast development and building
- **Data Processing**: Pandas for CSV loading and analysis

## Project Structure

```
lang-graph/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app and routes
│   │   ├── models.py            # Pydantic models
│   │   ├── pipeline/
│   │   │   ├── graph.py         # LangGraph definition
│   │   │   ├── nodes.py         # Pipeline nodes
│   │   │   └── state.py         # State schema
│   │   └── utils/
│   │       └── data_loader.py   # CSV utilities
│   └── .env.example
├── requirements.txt             # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   └── ResultsDisplay.jsx
│   │   └── services/
│   │       └── api.js
│   └── package.json
└── README.md
```

## Setup

### Backend Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `backend` directory:
```bash
# Copy the example file (if it exists) or create manually
# The .env file should be in backend/.env
```

5. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

6. Run the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Via API

Upload a CSV file using a POST request:

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_file.csv"
```

The response will be a JSON report containing:
- Schema profile (columns, types, null counts)
- Quality issues (detected problems)
- Explanations (LLM-generated explanations)
- Recommendations (suggested fixes)
- Summary statistics

### Via Frontend

1. Open `http://localhost:5173` in your browser
2. Drag and drop a CSV file or click to browse
3. Wait for the analysis to complete
4. Review the results in collapsible sections

## LangGraph Pipeline

The pipeline consists of the following nodes:

1. **load_data**: Validates CSV data is loaded
2. **profile_schema**: Analyzes column structure and statistics
3. **check_quality**: Detects data quality issues
4. **explain_issues**: Uses LLM to explain issues (conditional, only if issues exist)
5. **recommend_fixes**: Uses LLM to suggest fixes (conditional, only if issues exist)
6. **generate_report**: Compiles final structured report

The pipeline uses conditional edges to skip explanation/recommendation steps if no issues are detected.

## API Endpoints

- `GET /`: API information
- `GET /health`: Health check
- `POST /api/upload`: Upload CSV file for analysis

## Requirements

### Backend
- Python 3.8+
- FastAPI
- LangChain & LangGraph
- Pandas
- OpenAI API key

### Frontend
- Node.js 16+
- React 18+
- Vite

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for LLM features)

## License

MIT

