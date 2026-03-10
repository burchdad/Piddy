import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Tests() {
  const [tests, setTests] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const summaryData = await fetchApi('/api/tests/summary');
        setSummary(summaryData.summary || summaryData);
        
        const testsData = await fetchApi('/api/tests');
        setTests(Array.isArray(testsData) ? testsData : (testsData.tests || []));
      } catch (err) {
        console.error('Failed to fetch tests:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTests();
    const interval = setInterval(fetchTests, 10000);
    return () => clearInterval(interval);
  }, []);

  const filteredTests = filter === 'all' ? (Array.isArray(tests) ? tests : []) : (Array.isArray(tests) ? tests.filter(t => t.status === filter) : []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'passed': return '#51cf66';
      case 'failed': return '#ff6b6b';
      case 'skipped': return '#ffd93d';
      default: return '#cbd5e1';
    }
  };

  if (loading) return <div className="page">Loading tests...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>✅ Test Results</h1>
      </div>

      {summary && (
        <div className="summary-cards">
          <div className="summary-card passed">
            <div className="summary-value">{summary.passed}</div>
            <div className="summary-label">Passed</div>
          </div>
          <div className="summary-card failed">
            <div className="summary-value">{summary.failed}</div>
            <div className="summary-label">Failed</div>
          </div>
          <div className="summary-card skipped">
            <div className="summary-value">{summary.skipped}</div>
            <div className="summary-label">Skipped</div>
          </div>
          <div className="summary-card total">
            <div className="summary-value">{summary.total}</div>
            <div className="summary-label">Total</div>
          </div>
        </div>
      )}

      {summary && (
        <div className="progress-container">
          <div className="progress-bar">
            <div className="progress-fill passed" style={{width: `${(summary.passed / summary.total) * 100}%`}}></div>
            <div className="progress-fill failed" style={{width: `${(summary.failed / summary.total) * 100}%`}}></div>
            <div className="progress-fill skipped" style={{width: `${(summary.skipped / summary.total) * 100}%`}}></div>
          </div>
          <div className="progress-label">Pass Rate: {(summary.pass_rate ?? 0).toFixed(1)}%</div>
        </div>
      )}

      <div className="filter-buttons">
        <button className={`filter-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>All</button>
        <button className={`filter-btn ${filter === 'passed' ? 'active' : ''}`} onClick={() => setFilter('passed')}>Passed</button>
        <button className={`filter-btn ${filter === 'failed' ? 'active' : ''}`} onClick={() => setFilter('failed')}>Failed</button>
        <button className={`filter-btn ${filter === 'skipped' ? 'active' : ''}`} onClick={() => setFilter('skipped')}>Skipped</button>
      </div>

      <div className="tests-list">
        {Array.isArray(filteredTests) && filteredTests.map((test) => (
          <div key={test.test_id} className={`test-item ${test.status}`}>
            <div className="test-status" style={{backgroundColor: getStatusColor(test.status)}}>
              {test.status === 'passed' ? '✓' : test.status === 'failed' ? '✗' : '⊘'}
            </div>
            <div className="test-info">
              <div className="test-name">{test.test_name}</div>
              <div className="test-duration">{(test.duration_seconds ?? 0).toFixed(3)}s</div>
            </div>
            <div className="test-message">{test.message}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Tests;
