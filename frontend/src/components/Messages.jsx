import React, { useState, useEffect, useRef } from 'react';
import '../styles/components.css';

function Messages() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const messageEndRef = useRef(null);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/messages?limit=100');
        const data = await response.json();
        setMessages(data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch messages:', error);
        setLoading(false);
      }
    };

    fetchMessages();
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const filteredMessages = filter === 'all' 
    ? messages 
    : messages.filter(m => m.message_type === filter);

  const messageTypes = [...new Set(messages.map(m => m.message_type))];

  const getMessageIcon = (type) => {
    const icons = {
      proposal: '💡',
      vote: '🗳️',
      execute: '⚙️',
      report: '📋',
      query: '❓',
      alert: '⚠️'
    };
    return icons[type] || '📨';
  };

  const getPriorityColor = (priority) => {
    if (priority >= 8) return '#ff6b6b';
    if (priority >= 6) return '#ffa500';
    return '#51cf66';
  };

  return (
    <div className="page messages">
      <div className="header-section">
        <h2>💬 Agent Message Board</h2>
        <p className="subtitle">Real-time communication between autonomous agents (Read-only monitoring)</p>
      </div>

      <div className="controls">
        <div className="filter-group">
          <label>Filter by Type:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All Messages</option>
            {messageTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
        <p className="message-count">Total: {filteredMessages.length} messages</p>
      </div>

      {loading ? (
        <div className="loading">Loading messages...</div>
      ) : filteredMessages.length === 0 ? (
        <div className="empty-state">
          <p>No messages to display</p>
        </div>
      ) : (
        <div className="message-board">
          {filteredMessages.map((msg) => (
            <div key={msg.message_id} className="message-item">
              <div className="message-header">
                <div className="message-info">
                  <span className="message-icon">{getMessageIcon(msg.message_type)}</span>
                  <span className="message-type">{msg.message_type}</span>
                  <span className="message-sender">{msg.sender_id}</span>
                  {msg.receiver_id && (
                    <>
                      <span className="arrow">→</span>
                      <span className="message-receiver">{msg.receiver_id}</span>
                    </>
                  )}
                </div>
                <div className="message-meta">
                  <span className="priority" style={{ color: getPriorityColor(msg.priority) }}>
                    Priority: {msg.priority}
                  </span>
                  <span className="timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>

              <div className="message-content">
                <pre>{JSON.stringify(msg.content, null, 2)}</pre>
              </div>
            </div>
          ))}
          <div ref={messageEndRef} />
        </div>
      )}

      <div className="message-stats">
        <h3>Message Statistics</h3>
        <div className="stats-grid">
          <div className="stat">
            <label>By Type:</label>
            <div className="type-counts">
              {messageTypes.map(type => (
                <div key={type} className="type-count">
                  <span>{type}:</span>
                  <span className="count">{messages.filter(m => m.message_type === type).length}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Messages;
