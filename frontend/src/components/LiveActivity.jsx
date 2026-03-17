import React, { useEffect, useState, useRef } from 'react';
import { useStream } from '../hooks/useStream';
import '../styles/components.css';

/**
 * LiveActivity - Real-time agent activity visualization
 * 
 * Shows actual work happening:
 * - Nova commands executing
 * - Agent decisions being made
 * - Progress updates in real-time
 * - Task completions with results
 * 
 * NOT mock data - real events from the coordinator
 */
function LiveActivity() {
  const activitiesEndRef = useRef(null);
  const [activeAgents, setActiveAgents] = useState(new Set());

  // Stream real agent activity
  const { 
    data: activities, 
    isLoading, 
    error: streamError,
    pause,
    resume
  } = useStream('stream.agent_activity', [50], {}, {
    maxItems: 50,
    onData: (activity) => {
      // Track which agents are active
      if (activity.agent) {
        setActiveAgents(prev => new Set([...prev, activity.agent]));
        // Remove from active after 10 seconds of no updates
        setTimeout(() => {
          setActiveAgents(prev => {
            const updated = new Set(prev);
            updated.delete(activity.agent);
            return updated;
          });
        }, 10000);
      }
    }
  });

  // Auto-scroll to latest activity
  useEffect(() => {
    if (activitiesEndRef.current) {
      activitiesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activities.length]);

  // Get status badge color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'in_progress':
        return '#3b82f6';
      case 'failed':
        return '#ef4444';
      case 'paused':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  // Get status emoji
  const getStatusEmoji = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'in_progress':
        return '🔄';
      case 'failed':
        return '❌';
      case 'paused':
        return '⏸️';
      default:
        return '📋';
    }
  };

  return (
    <div className="page live-activity-container">
      <h2>🔴 Live Agent Activity Stream</h2>
      
      {/* Live Status */}
      <div className="activity-status-bar">
        <div className="live-indicator">
          <span className="live-pulse">🔴</span> LIVE
        </div>
        {isLoading && activities.length === 0 ? (
          <span className="status">🔄 Connecting to activity stream...</span>
        ) : (
          <span className="status">
            📊 {activities.length} events | 👥 {activeAgents.size} agents active
          </span>
        )}
        {streamError && (
          <span className="status-error">⚠️ {streamError}</span>
        )}
      </div>

      {/* Activity Timeline */}
      <div className="activity-timeline">
        {activities.length === 0 ? (
          <div className="activity-empty">
            <p>Waiting for agent activity...</p>
            <small>Activity will appear here as agents work on tasks</small>
          </div>
        ) : (
          activities.map((activity, idx) => (
            <div 
              key={activity.id || idx}
              className={`activity-item ${activity.status} ${activity.LIVE ? 'live-update' : ''}`}
            >
              {/* Status indicator */}
              <div className="activity-indicator" style={{ backgroundColor: getStatusColor(activity.status) }}>
                {getStatusEmoji(activity.status)}
              </div>

              {/* Activity details */}
              <div className="activity-details">
                <div className="activity-header">
                  <span className="agent-name">{activity.agent}</span>
                  <span className="action-name">{activity.action}</span>
                  <span className="timestamp">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {activity.description && (
                  <div className="activity-description">{activity.description}</div>
                )}

                {/* Progress bar for in-progress items */}
                {activity.status === 'in_progress' && activity.progress_percent !== undefined && (
                  <div className="progress-container">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${activity.progress_percent}%` }}
                      />
                    </div>
                    <span className="progress-text">{activity.progress_percent.toFixed(0)}%</span>
                  </div>
                )}

                {/* Duration for completed items */}
                {activity.status === 'completed' && activity.duration_ms && (
                  <div className="activity-duration">
                    ⏱️ {(activity.duration_ms / 1000).toFixed(2)}s
                  </div>
                )}

                {/* Result summary for completed items */}
                {activity.result && (
                  <div className="activity-result">
                    ✨ Result: {typeof activity.result === 'string' ? activity.result : JSON.stringify(activity.result).substring(0, 100)}...
                  </div>
                )}

                {/* Status badge */}
                <div className="status-badge" style={{ borderColor: getStatusColor(activity.status) }}>
                  {activity.status.toUpperCase()}
                </div>
              </div>

              {/* Live indicator */}
              {activity.LIVE && (
                <div className="live-animation">
                  <span>🟢 NOW</span>
                </div>
              )}
            </div>
          ))
        )}

        {/* Scroll anchor */}
        <div ref={activitiesEndRef} />
      </div>

      {/* Legend */}
      <div className="activity-legend">
        <div className="legend-item">✅ Completed - Task finished successfully</div>
        <div className="legend-item">🔄 In Progress - Task currently running</div>
        <div className="legend-item">❌ Failed - Task encountered an error</div>
        <div className="legend-item">⏸️ Paused - Task temporarily stopped</div>
        <div className="legend-item">🟢 NOW - Real-time activity happening</div>
      </div>

      {/* Debug Info */}
      <div className="activity-debug">
        <small>
          Stream: stream.agent_activity | Items: {activities.length} | 
          {isLoading ? ' Loading...' : ' Connected'} | 
          Active Agents: {Array.from(activeAgents).join(', ') || 'None'}
        </small>
      </div>
    </div>
  );
}

export default LiveActivity;
