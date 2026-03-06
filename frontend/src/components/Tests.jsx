import React, { useState, useEffect } from 'react';
import '../styles/components.css';

function Tests() {
  const [tests, setTests] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const [testsResponse, summaryResponse] = await Promise.all([
          fetch('http://127.0.0.1:8000/api/tests'),
          fetch('http://127.0.0.1:8000/api/tests/summary')
        ]);
        
        const testsData = await testsResponse.json();
        const summaryData = await summaryResponse.json();
        
        setTests(testsData);
        setSummary(summaryData);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch tests:', error);
        setLoading(false);
      }
    };

    fetchTests();
    const interval = setInterval(fetchTests, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    const icons = {
      passed: '✅',
      failed: '❌',
      skipped: '⏭️'
    };
    return icons[status] || '❓';
  };

  const getStatusColor = (status) => {
    const colors = {
      passed: '#51cf66',
      failed: '#ff6b6b',
      skipped: '#a6a6a6'
    };
    return colors[status] || '#333';
  };

  return (
    <div className="page tests">
      <div className="header-section">
        <h2>🧪 Test Results</h2>
        <p className="subtitle">Automated test execution and results</p>
      </div>

      {loading ? (
        <div className="loading">Loading test results...</div>
      ) : (
        <>
          {summary && (
            <div className="test-summary">
              <div className="summary-card">
                <div className="summary-title">Total Tests</div>
                <div className="summary-value">{summary.total}</div>
              </div>

              <div className="summary-card passed">
                <div className="summary-title">Passed</div>
                <div className="summary-value" style={{ color: '#51cf66' }}>{summary.passed}</div>
              </div>

              <div className="summary-card failed">
                <div className="summary-title">Failed</div>
                <div className="summary-value" style={{ color: '#ff6b6b' }}>{summary.failed}</div>
              </div>

              <div className="summary-card">
                <div className="summary-title">Pass Rate</div>
                <div className="summary-value" style={{ color: summary.pass_rate >= 95 ? '#51cf66' : '#ffa500' }}>
                  {summary.pass_rate.toFixed(1)}%
                </div>
              </div>
            </div>
          )}

          <div className="test-list">
            <h3>Test Details</h3>
            {tests.map((test) => (
              <div key={test.test_id} className={`test-item ${test.status}`}>
                <div className="test-header">
                  <span className="test-status" style={{ color: getStatusColor(test.status) }}>
                    {getStatusIcon(test.status)}
                  </span>
                  <span className="test-name">{test.test_name}</span>
                  <span className="test-duration">{test.duration_seconds.toFixed(3)}s</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default Tests;
