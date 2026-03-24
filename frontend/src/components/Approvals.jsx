import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import { useToast } from './Toast';
import '../styles/components.css';

function Approvals() {
  const [approvals, setApprovals] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedRequest, setExpandedRequest] = useState(null);
  const [expandedGap, setExpandedGap] = useState({});
  const [processingGap, setProcessingGap] = useState(null);
  const [processingRequest, setProcessingRequest] = useState(null);
  const [rejectionReason, setRejectionReason] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);
  const toast = useToast();

  // Fetch approvals and stats
  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        setLoading(true);
        const [approvalsData, statsData] = await Promise.all([
          fetchApi('/api/approvals'),
          fetchApi('/api/approvals/summary/stats')
        ]);
        
        setApprovals(
          approvalsData.requests 
            ? Object.values(approvalsData.requests)
            : (Array.isArray(approvalsData) ? approvalsData : [])
        );
        setStats(statsData);
        setErrorMessage(null);
      } catch (err) {
        console.error('Failed to fetch approvals:', err);
        setErrorMessage('Failed to load approval requests');
      } finally {
        setLoading(false);
      }
    };

    fetchApprovals();
    const interval = setInterval(fetchApprovals, 10000);
    return () => clearInterval(interval);
  }, []);

  const refreshApprovals = async () => {
    const [approvalsData, statsData] = await Promise.all([
      fetchApi('/api/approvals'),
      fetchApi('/api/approvals/summary/stats')
    ]);
    setApprovals(
      approvalsData.requests 
        ? Object.values(approvalsData.requests)
        : (Array.isArray(approvalsData) ? approvalsData : [])
    );
    setStats(statsData);
  };

  // Request-level actions
  const handleApproveRequest = async (requestId) => {
    try {
      setProcessingRequest(requestId);
      await fetchApi('/api/approvals/approve', 'POST', { request_id: requestId });
      toast.success(`Request ${requestId} fully approved`);
      await refreshApprovals();
    } catch (err) {
      console.error('Failed to approve request:', err);
      toast.error(`Failed to approve request: ${err.message}`);
    } finally {
      setProcessingRequest(null);
    }
  };

  const handleRejectRequest = async (requestId) => {
    try {
      setProcessingRequest(requestId);
      await fetchApi('/api/approvals/reject', 'POST', { request_id: requestId, reason: 'Rejected by reviewer' });
      toast.warning(`Request ${requestId} rejected`);
      await refreshApprovals();
    } catch (err) {
      console.error('Failed to reject request:', err);
      toast.error(`Failed to reject request: ${err.message}`);
    } finally {
      setProcessingRequest(null);
    }
  };

  const handleApprove = async (requestId, gapId) => {
    try {
      setProcessingGap(`${requestId}-${gapId}`);
      await fetchApi(
        '/api/approvals/gap/approve',
        'POST',
        { request_id: requestId, gap_id: gapId }
      );
      toast.success(`Gap ${gapId} approved!`);
      await refreshApprovals();
    } catch (err) {
      console.error('Failed to approve gap:', err);
      setErrorMessage(`Failed to approve gap: ${err.message}`);
    } finally {
      setProcessingGap(null);
    }
  };

  const handleReject = async (requestId, gapId) => {
    try {
      setProcessingGap(`${requestId}-${gapId}`);
      const reason = rejectionReason[`${requestId}-${gapId}`] || 'No reason provided';
      await fetchApi(
        '/api/approvals/gap/reject',
        'POST',
        { request_id: requestId, gap_id: gapId, reason }
      );
      toast.warning(`Gap ${gapId} rejected`);
      setRejectionReason(prev => {
        const newReason = {...prev};
        delete newReason[`${requestId}-${gapId}`];
        return newReason;
      });
      await refreshApprovals();
    } catch (err) {
      console.error('Failed to reject gap:', err);
      setErrorMessage(`Failed to reject gap: ${err.message}`);
    } finally {
      setProcessingGap(null);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel.toUpperCase()) {
      case 'HIGH':
        return '#e74c3c';
      case 'MEDIUM':
        return '#f39c12';
      case 'LOW':
        return '#27ae60';
      default:
        return '#3498db';
    }
  };

  const getRiskBadgeClass = (riskLevel) => {
    switch (riskLevel.toUpperCase()) {
      case 'HIGH':
        return 'risk-high';
      case 'MEDIUM':
        return 'risk-medium';
      case 'LOW':
        return 'risk-low';
      default:
        return 'risk-unknown';
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="section-header">
          <h1>📋 Market Gap Approvals</h1>
        </div>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading approval requests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="section-header">
        <h1>📋 Market Gap Approvals</h1>
        <p className="section-description">Review and approve/reject market gaps for autonomous building</p>
      </div>

      {/* Statistics Card */}
      {stats && (
        <div className="approval-stats">
          <div className="stat-card">
            <div className="stat-label">Total Decisions</div>
            <div className="stat-value">{stats.total_decisions || 0}</div>
          </div>
          <div className="stat-card stat-approved">
            <div className="stat-label">Approved</div>
            <div className="stat-value">{stats.approved_count || 0}</div>
          </div>
          <div className="stat-card stat-rejected">
            <div className="stat-label">Rejected</div>
            <div className="stat-value">{stats.rejected_count || 0}</div>
          </div>
          <div className="stat-card stat-pending">
            <div className="stat-label">Pending Requests</div>
            <div className="stat-value">{stats.pending_requests || 0}</div>
          </div>
          <div className="stat-card stat-rate">
            <div className="stat-label">Approval Rate</div>
            <div className="stat-value">{(stats.approval_rate || 0).toFixed(1)}%</div>
          </div>
        </div>
      )}

      {/* Messages */}
      {errorMessage && (
        <div className="message message-error">
          {errorMessage}
        </div>
      )}

      {/* Approvals List */}
      <div className="approvals-list">
        {approvals && approvals.length > 0 ? (
          approvals.map((request) => (
            <div key={request.request_id} className="approval-request-card">
              {/* Request Header */}
              <div 
                className="request-header"
                onClick={() => setExpandedRequest(
                  expandedRequest === request.request_id ? null : request.request_id
                )}
              >
                <div className="request-info">
                  <div className="request-id">
                    <span className="request-label">Request ID:</span>
                    <code>{request.request_id}</code>
                  </div>
                  <div className="request-status">
                    <span className={`status-badge status-${request.status}`}>
                      {request.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* Risk Summary */}
                <div className="risk-summary">
                  {request.high_risk_count > 0 && (
                    <div className="risk-count high-risk">
                      <span className="risk-icon">⚠️ HIGH</span>
                      <span className="risk-number">{request.high_risk_count}</span>
                    </div>
                  )}
                  {request.medium_risk_count > 0 && (
                    <div className="risk-count medium-risk">
                      <span className="risk-icon">⚡ MEDIUM</span>
                      <span className="risk-number">{request.medium_risk_count}</span>
                    </div>
                  )}
                  {request.low_risk_count > 0 && (
                    <div className="risk-count low-risk">
                      <span className="risk-icon">✓ LOW</span>
                      <span className="risk-number">{request.low_risk_count}</span>
                    </div>
                  )}
                </div>

                <div className="expand-icon">
                  {expandedRequest === request.request_id ? '▼' : '▶'}
                </div>
              </div>

              {/* Request Action Buttons */}
              <div className="request-actions">
                <button
                  className="btn btn-review"
                  onClick={(e) => {
                    e.stopPropagation();
                    setExpandedRequest(
                      expandedRequest === request.request_id ? null : request.request_id
                    );
                  }}
                  title="Review gaps in this request"
                >
                  🔍 Review
                </button>
                <button
                  className="btn btn-approve-request"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleApproveRequest(request.request_id);
                  }}
                  disabled={processingRequest === request.request_id || request.status === 'fully_approved'}
                  title="Approve all gaps in this request"
                >
                  {processingRequest === request.request_id ? '⏳' : '✅'} Approve
                </button>
                <button
                  className="btn btn-deny-request"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRejectRequest(request.request_id);
                  }}
                  disabled={processingRequest === request.request_id || request.status === 'rejected'}
                  title="Deny all gaps in this request"
                >
                  {processingRequest === request.request_id ? '⏳' : '❌'} Deny
                </button>
              </div>

              {/* Expanded Content */}
              {expandedRequest === request.request_id && (
                <div className="request-details">
                  <div className="request-meta">
                    <div className="meta-item">
                      <span className="meta-label">Created:</span>
                      <span className="meta-value">
                        {new Date(request.created_at || request.sent_at).toLocaleString()}
                      </span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Deadline:</span>
                      <span className="meta-value">
                        {new Date(request.deadline || request.approval_deadline).toLocaleString()}
                      </span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Sent To:</span>
                      <span className="meta-value">
                        {request.sent_to_emails?.join(', ') || 'You (Reviewer)'}
                      </span>
                    </div>

                    {/* Gaps summary */}
                    <div className="meta-item">
                      <span className="meta-label">Gaps:</span>
                      <span className="meta-value">
                        {request.market_gaps?.length || 0} total
                        {request.approved_gaps?.length > 0 && ` · ${request.approved_gaps.length} approved`}
                        {request.rejected_gaps?.length > 0 && ` · ${request.rejected_gaps.length} rejected`}
                      </span>
                    </div>
                  </div>

                  {/* Gaps List */}
                  <div className="gaps-container">
                    {(request.market_gaps || request.gaps || []).map((gap) => (
                      <div
                        key={`${request.request_id}-${gap.gap_id}`}
                        className="gap-card"
                      >
                        {/* Gap Header */}
                        <div
                          className="gap-header"
                          onClick={() => {
                            const key = `${request.request_id}-${gap.gap_id}`;
                            setExpandedGap(prev => ({
                              ...prev,
                              [key]: !prev[key]
                            }));
                          }}
                        >
                          <div className="gap-title-section">
                            <span className={`risk-badge ${getRiskBadgeClass(gap.security_risk_level)}`}>
                              {gap.security_risk_level}
                            </span>
                            <span className="gap-title">{gap.title}</span>
                            <span className="gap-category">{gap.category}</span>
                          </div>
                          <span className="expand-icon">
                            {expandedGap[`${request.request_id}-${gap.gap_id}`] ? '▼' : '▶'}
                          </span>
                        </div>

                        {/* Gap Details */}
                        {expandedGap[`${request.request_id}-${gap.gap_id}`] && (
                          <div className="gap-details">
                            <div className="gap-info">
                              <div className="info-row">
                                <span className="info-label">Gap ID:</span>
                                <code className="info-value">{gap.gap_id}</code>
                              </div>
                              <div className="info-row">
                                <span className="info-label">Category:</span>
                                <span className="info-value">{gap.category}</span>
                              </div>
                              <div className="info-row">
                                <span className="info-label">Market Need:</span>
                                <span className="info-value">{gap.market_need}</span>
                              </div>
                              <div className="info-row">
                                <span className="info-label">Frequency:</span>
                                <span className="info-value">{gap.frequency}x</span>
                              </div>
                              <div className="info-row">
                                <span className="info-label">Estimated Impact:</span>
                                <span className="info-value">{(gap.estimated_impact * 100).toFixed(1)}%</span>
                              </div>
                              <div className="info-row">
                                <span className="info-label">Complexity:</span>
                                <span className="info-value">{gap.complexity_score}/10</span>
                              </div>
                              <div className="info-row">
                                <span className="info-label">Est. Build Time:</span>
                                <span className="info-value">{gap.estimated_build_time_hours}h</span>
                              </div>
                            </div>

                            {/* Security Assessment */}
                            {gap.security_concerns && gap.security_concerns.length > 0 && (
                              <div className="security-section">
                                <h4>🔒 Security Concerns ({gap.security_concerns.length})</h4>
                                <ul className="concerns-list">
                                  {gap.security_concerns.map((concern, idx) => (
                                    <li key={idx} className="concern-item">
                                      {concern}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Integration Points */}
                            {gap.integration_points && gap.integration_points.length > 0 && (
                              <div className="integration-section">
                                <h4>🔗 Integration Points ({gap.integration_points.length})</h4>
                                <ul className="integration-list">
                                  {gap.integration_points.map((point, idx) => (
                                    <li key={idx} className="integration-item">
                                      {point}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Decision Section */}
                            <div className="gap-decision">
                              <div className="decision-label">Your Decision:</div>
                              
                              {/* Rejection Reason Input */}
                              <div className="rejection-reason">
                                <textarea
                                  placeholder="Reason for rejection (optional, required if rejecting)..."
                                  value={rejectionReason[`${request.request_id}-${gap.gap_id}`] || ''}
                                  onChange={(e) => {
                                    const key = `${request.request_id}-${gap.gap_id}`;
                                    setRejectionReason(prev => ({
                                      ...prev,
                                      [key]: e.target.value
                                    }));
                                  }}
                                  className="reason-text"
                                />
                              </div>

                              <div className="decision-buttons">
                                <button
                                  className="btn btn-approve"
                                  onClick={() => handleApprove(request.request_id, gap.gap_id)}
                                  disabled={processingGap === `${request.request_id}-${gap.gap_id}`}
                                >
                                  {processingGap === `${request.request_id}-${gap.gap_id}` ? (
                                    '⏳ Approving...'
                                  ) : (
                                    '✅ Approve'
                                  )}
                                </button>
                                <button
                                  className="btn btn-reject"
                                  onClick={() => handleReject(request.request_id, gap.gap_id)}
                                  disabled={processingGap === `${request.request_id}-${gap.gap_id}`}
                                >
                                  {processingGap === `${request.request_id}-${gap.gap_id}` ? (
                                    '⏳ Rejecting...'
                                  ) : (
                                    '❌ Reject'
                                  )}
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No Approval Requests</h3>
            <p>There are currently no pending market gap approvals.</p>
            {stats && (
              <div className="empty-stats">
                <p>You've reviewed <strong>{stats.total_decisions || 0}</strong> gaps</p>
                <p>Approval rate: <strong>{(stats.approval_rate || 0).toFixed(1)}%</strong></p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Approvals;
