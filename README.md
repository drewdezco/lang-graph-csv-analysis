# CSV Data Quality Analysis Service

A FastAPI + LangGraph service that ingests a CSV, profiles its schema, runs quality checks, and uses an LLM to explain detected issues and recommend fixes — returned as a single structured JSON report. Ships with a React frontend for upload and visualization.

## Why it's interesting

The analysis runs as a **LangGraph pipeline with conditional routing**: if the quality checks find no issues, the graph skips the LLM nodes entirely and goes straight to report generation. That keeps cost and latency low on clean files, and reserves model calls for the cases where natural-language explanation actually adds value.

```
load_data → profile_schema → check_quality
                                  │
                          issues found?
                          ├── yes → explain_issues → recommend_fixes → generate_report
                          └── no  ─────────────────────────────────→ generate_report
```

## What it detects

- Null counts and missing values
- Duplicate rows
- Type mismatches (inferred vs. declared)
- Schema profile per column (dtype, null %, sample values)

For each issue, the LLM nodes produce a plain-language explanation and a recommended remediation.

## Stack

- **Backend:** FastAPI, LangGraph, LangChain, OpenAI, pandas
- **Frontend:** React 18 + Vite
- **Pipeline:** LangGraph state machine with conditional edges

## Quickstart

```bash
# Backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > backend/.env
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev          # http://localhost:5173
```

## API

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@mock_data.csv"
```

Returns a JSON report with `schema_profile`, `issues`, `explanations`, `recommendations`, and `summary`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/api/upload` | POST | Upload CSV, run analysis |

## Project layout

```
backend/app/
  main.py              FastAPI routes
  models.py            Pydantic schemas
  pipeline/
    graph.py           LangGraph definition + conditional edges
    nodes.py           load / profile / check / explain / recommend / report
    state.py           Shared pipeline state
  utils/data_loader.py CSV parsing helpers
frontend/src/
  App.jsx
  components/          FileUpload, ResultsDisplay
  services/api.js
```

## Requirements

- Python 3.8+
- Node.js 16+
- OpenAI API key (for `explain_issues` and `recommend_fixes` nodes)

## License

MIT
