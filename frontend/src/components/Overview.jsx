import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Overview({ systemStatus }) {
  const [selectedMetric, setSelectedMetric] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [approvalLoading, setApprovalLoading] = useState(null);
  const [decisions, setDecisions] = useState([]);
  const [agents, setAgents] = useState([]);
  const [missions, setMissions] = useState([]);

  useEffect(() => {
    // Fetch all detail data on mount
    const fetchAllData = async () => {
      try {
        const [decisionsData, agentsData, missionsData] = await Promise.all([
          fetchApi('/api/decisions').catch(() => ({ decisions: [] })),
          fetchApi('/api/agents').catch(() => ({ agents: [] })),
          fetchApi('/api/missions').catch(() => ({ missions: [] }))
        ]);
        
        setDecisions(Array.isArray(decisionsData) ? decisionsData : (decisionsData.decisions || []));
        setAgents(Array.isArray(agentsData) ? agentsData : (agentsData.agents || []));
        setMissions(Array.isArray(missionsData) ? missionsData : (missionsData.missions || []));
      } catch (err) {
        console.error('Failed to fetch detail data:', err);
      }
    };
    
    fetchAllData();
  }, []);

  const handleMetricClick = async (metric) => {
    setSelectedMetric(metric);
    setDetailData(null);
    setLoadingDetail(true);

    // Prepare detail data based on metric type
    switch(metric) {
      case 'status':
        setDetailData({
          label: 'System Status',
          value: systemStatus?.status,
          color: systemStatus?.status === 'operational' ? '#51cf66' : '#ff6b6b',
          details: [
            { label: 'Status', value: systemStatus?.status },
            { label: 'Last Updated', value: new Date(systemStatus?.last_updated).toLocaleString() },
            { label: 'Uptime', value: systemStatus?.uptime_hours ? `${systemStatus.uptime_hours}h` : 'N/A' }
          ]
        });
        break;
      case 'agents':
        setDetailData({
          label: 'Agents Online',
          value: systemStatus?.agents_online,
          items: agents,
          itemsLabel: 'agents'
        });
        break;
      case 'missions':
        setDetailData({
          label: 'Active Missions',
          value: systemStatus?.missions_active,
          items: missions.filter(m => m.status === 'in_progress'),
          itemsLabel: 'missions'
        });
        break;
      case 'decisions':
        setDetailData({
          label: 'Pending Decisions',
          value: systemStatus?.decisions_pending,
          items: decisions.filter(d => d.status === 'pending'),
          itemsLabel: 'decisions',
          isDecisions: true
        });
        break;
      default:
        break;
    }
    setLoadingDetail(false);
  };

  const handleApproveDecision = async (decisionId, approved) => {
    setApprovalLoading(decisionId);
    try {
      const response = await fetchApi(
        `/api/decisions/${decisionId}/${approved ? 'approve' : 'reject'}`,
        { method: 'POST' }
      );
      
      // Update the decisions list
      setDecisions(decisions.map(d => 
        d.id === decisionId 
          ? { ...d, status: approved ? 'approved' : 'rejected' }
          : d
      ));
      
      console.log(`✅ Decision ${approved ? 'approved' : 'rejected'}`);
    } catch (err) {
      console.error('Failed to update decision:', err);
    } finally {
      setApprovalLoading(null);
    }
  };

  const closeModal = () => {
    setSelectedMetric(null);
    setDetailData(null);
  };

  if (!systemStatus) {
    return <div className="page"><h2>Loading...</h2></div>;
  }

  return (
    <div className="page overview">
      <div className="header-section">
        <div className="header-content">
          <h2>System Overview</h2>
          <p className="timestamp">
            Last updated: {new Date(systemStatus.last_updated).toLocaleString()}
          </p>
        </div>
        <div className="status-badge">
          <span className="badge-dot" style={{ 
            backgroundColor: systemStatus.status === 'operational' ? '#51cf66' : '#ff6b6b' 
          }}></span>
          <span>{systemStatus.status.toUpperCase()}</span>
        </div>
      </div>

      <div className="metrics-grid">
        <div 
          className="metric-card metric-card-interactive"
          onClick={() => handleMetricClick('status')}
        >
          <div className="metric-icon">⚙️</div>
          <div className="metric-label">System Status</div>
          <div className="metric-value" style={{ 
            color: systemStatus.status === 'operational' ? '#51cf66' : '#ff6b6b' 
          }}>
            {systemStatus.status}
          </div>
          <div className="metric-sub">Click to see details</div>
        </div>

        <div 
          className="metric-card metric-card-interactive"
          onClick={() => handleMetricClick('agents')}
        >
          <div className="metric-icon">🤖</div>
          <div className="metric-label">Agents Online</div>
          <div className="metric-value">{systemStatus.agents_online}</div>
          <div className="metric-sub">Available agents</div>
        </div>

        <div 
          className="metric-card metric-card-interactive"
          onClick={() => handleMetricClick('missions')}
        >
          <div className="metric-icon">🎯</div>
          <div className="metric-label">Active Missions</div>
          <div className="metric-value">{systemStatus.missions_active}</div>
          <div className="metric-sub">In progress</div>
        </div>

        <div 
          className="metric-card metric-card-interactive pending"
          onClick={() => handleMetricClick('decisions')}
        >
          <div className="metric-icon">✓</div>
          <div className="metric-label">Pending Decisions</div>
          <div className="metric-value">{systemStatus.decisions_pending}</div>
          <div className="metric-sub">Awaiting approval</div>
        </div>
      </div>

      <div className="status-section">
        <h3>System Health</h3>
        <div className="health-indicator">
          <div className="indicator-item">
            <span className="indicator-dot" style={{ backgroundColor: '#51cf66' }}></span>
            <span>All systems operational</span>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedMetric && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{detailData?.label}</h2>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>

            <div className="modal-body">
              {loadingDetail ? (
                <div className="loading-spinner">Loading...</div>
              ) : detailData?.isDecisions ? (
                <div className="decisions-drill">
                  {detailData.items && detailData.items.length > 0 ? (
                    detailData.items.map((decision) => (
                      <div key={decision.id} className="drill-item decision-item">
                        <div className="item-header">
                          <div className="item-title">{decision.task}</div>
                          <div className="item-confidence">
                            {((decision.confidence ?? 0) * 100).toFixed(0)}% confident
                          </div>
                        </div>
                        <div className="item-action">{decision.action}</div>
                        {decision.reasoning_chain && (
                          <div className="item-reasoning">
                            <strong>Reasoning:</strong>
                            {Array.isArray(decision.reasoning_chain) && 
                              decision.reasoning_chain.slice(0, 2).map((step, idx) => (
                                <div key={idx} className="reasoning-item">
                                  • {step.thought || step}
                                </div>
                              ))
                            }
                          </div>
                        )}
                        <div className="approval-buttons">
                          <button 
                            className="btn-approve"
                            onClick={() => handleApproveDecision(decision.id, true)}
                            disabled={approvalLoading === decision.id}
                          >
                            ✓ Approve
                          </button>
                          <button 
                            className="btn-reject"
                            onClick={() => handleApproveDecision(decision.id, false)}
                            disabled={approvalLoading === decision.id}
                          >
                            ✕ Reject
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="empty-state">✓ No pending decisions</div>
                  )}
                </div>
              ) : detailData?.items ? (
                <div className="items-drill">
                  {detailData.items.map((item, idx) => (
                    <div key={item.id || idx} className="drill-item">
                      <div className="item-title">
                        {item.name || item.title || `${detailData.itemsLabel.slice(0, -1)} ${idx + 1}`}
                      </div>
                      <div className="item-status">
                        <span className="status-badge" style={{ 
                          backgroundColor: item.status === 'active' || item.status === 'in_progress' || item.status === 'online' 
                            ? '#51cf66' 
                            : '#ffd93d' 
                        }}>
                          {item.status || item.state}
                        </span>
                      </div>
                      {(item.reputation || item.progress) && (
                        <div className="item-details">
                          {item.reputation && <span>Reputation: {(item.reputation * 100).toFixed(0)}%</span>}
                          {item.progress && <span>Progress: {(item.progress * 100).toFixed(0)}%</span>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="detail-info">
                  {detailData?.details && detailData.details.map((detail, idx) => (
                    <div key={idx} className="detail-row">
                      <span className="detail-label">{detail.label}:</span>
                      <span className="detail-value">{detail.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn-close" onClick={closeModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Overview;
