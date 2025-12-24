import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ResultsDisplay from './components/ResultsDisplay';
import { uploadCSV } from './services/api';
import './App.css';

function App() {
  const [report, setReport] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = async (file) => {
    setIsUploading(true);
    setError(null);
    setReport(null);

    try {
      const analysisReport = await uploadCSV(file);
      setReport(analysisReport);
    } catch (err) {
      setError(err.message || 'Failed to analyze CSV file');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setReport(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>CSV Data Quality Analysis</h1>
        <p>Upload a CSV file to analyze data quality, detect issues, and get recommendations</p>
      </header>

      <main className="app-main">
        {!report && (
          <FileUpload
            onFileSelect={handleFileSelect}
            isUploading={isUploading}
          />
        )}

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={handleReset} className="reset-button">
              Try Again
            </button>
          </div>
        )}

        {report && (
          <>
            <div className="results-actions">
              <button onClick={handleReset} className="reset-button">
                Analyze Another File
              </button>
            </div>
            <ResultsDisplay report={report} />
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI, LangGraph, and LangChain</p>
      </footer>
    </div>
  );
}

export default App;

