import React, { useState } from 'react';
import './ResultsDisplay.css';

const ResultsDisplay = ({ report }) => {
  const [expandedSections, setExpandedSections] = useState({
    schema: true,
    issues: true,
    explanations: false,
    recommendations: false,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  if (!report) {
    return null;
  }

  const { schema_profile, quality_issues, explanations, recommendations, summary } = report;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Analysis Report</h2>
        {summary && (
          <div className="summary-badges">
            <span className="badge">Rows: {summary.total_rows}</span>
            <span className="badge">Columns: {summary.total_columns}</span>
            <span className="badge">Issues: {summary.total_issues}</span>
          </div>
        )}
      </div>

      {/* Schema Profile Section */}
      <div className="result-section">
        <button
          className="section-header"
          onClick={() => toggleSection('schema')}
        >
          <span className="section-title">
            <span className="section-icon">{expandedSections.schema ? '▼' : '▶'}</span>
            Schema Profile
          </span>
        </button>
        {expandedSections.schema && schema_profile && (
          <div className="section-content">
            <div className="schema-table-container">
              <table className="schema-table">
                <thead>
                  <tr>
                    <th>Column</th>
                    <th>Data Type</th>
                    <th>Null Count</th>
                    <th>Null %</th>
                    <th>Sample Values</th>
                  </tr>
                </thead>
                <tbody>
                  {schema_profile.columns.map((col) => (
                    <tr key={col}>
                      <td><strong>{col}</strong></td>
                      <td><code>{schema_profile.column_types[col]}</code></td>
                      <td>{schema_profile.null_counts[col]}</td>
                      <td>{schema_profile.null_percentages[col].toFixed(2)}%</td>
                      <td>
                        <div className="sample-values">
                          {schema_profile.sample_values[col]?.slice(0, 3).map((val, idx) => (
                            <span key={idx} className="sample-value">{String(val)}</span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Quality Issues Section */}
      {quality_issues && quality_issues.length > 0 && (
        <div className="result-section">
          <button
            className="section-header"
            onClick={() => toggleSection('issues')}
          >
            <span className="section-title">
              <span className="section-icon">{expandedSections.issues ? '▼' : '▶'}</span>
              Quality Issues ({quality_issues.length})
            </span>
          </button>
          {expandedSections.issues && (
            <div className="section-content">
              <div className="issues-list">
                {quality_issues.map((issue, idx) => (
                  <div key={idx} className="issue-card">
                    <div className="issue-header">
                      <span
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(issue.severity) }}
                      >
                        {issue.severity.toUpperCase()}
                      </span>
                      <span className="issue-type">{issue.issue_type}</span>
                      {issue.column && (
                        <span className="issue-column">Column: {issue.column}</span>
                      )}
                    </div>
                    <p className="issue-description">{issue.description}</p>
                    {issue.affected_rows !== undefined && (
                      <p className="issue-details">Affected Rows: {issue.affected_rows}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Explanations Section */}
      {explanations && explanations.length > 0 && (
        <div className="result-section">
          <button
            className="section-header"
            onClick={() => toggleSection('explanations')}
          >
            <span className="section-title">
              <span className="section-icon">{expandedSections.explanations ? '▼' : '▶'}</span>
              Issue Explanations ({explanations.length})
            </span>
          </button>
          {expandedSections.explanations && (
            <div className="section-content">
              <div className="explanations-list">
                {explanations.map((explanation, idx) => {
                  const issue = quality_issues.find(i => i.issue_id === explanation.issue_id);
                  return (
                    <div key={idx} className="explanation-card">
                      <h4>{issue?.description || explanation.issue_id}</h4>
                      <p>{explanation.explanation}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations Section */}
      {recommendations && recommendations.length > 0 && (
        <div className="result-section">
          <button
            className="section-header"
            onClick={() => toggleSection('recommendations')}
          >
            <span className="section-title">
              <span className="section-icon">{expandedSections.recommendations ? '▼' : '▶'}</span>
              Fix Recommendations ({recommendations.length})
            </span>
          </button>
          {expandedSections.recommendations && (
            <div className="section-content">
              <div className="recommendations-list">
                {recommendations.map((rec, idx) => {
                  const issue = quality_issues.find(i => i.issue_id === rec.issue_id);
                  return (
                    <div key={idx} className="recommendation-card">
                      <h4>{issue?.description || rec.issue_id}</h4>
                      <p>{rec.recommendation}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {quality_issues && quality_issues.length === 0 && (
        <div className="no-issues">
          <p>✓ No quality issues detected! Your data looks good.</p>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;

