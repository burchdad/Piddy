import React, { useEffect, useState, useRef } from 'react';
import { useStream } from '../hooks/useStream';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

/**
 * LiveChat - Real-time conversation with Piddy
 * 
 * Features:
 * - Live streaming messages (not fetched once)
 * - Real-time input to send commands to Piddy
 * - Timestamps and sender information
 * - Visual indicators for message status
 * - Auto-scroll to latest messages
 */
function LiveChat() {
  const [inputValue, setInputValue] = useState('');
  const [sendStatus, setSendStatus] = useState('');
  const messagesEndRef = useRef(null);
  const [userSendCount, setUserSendCount] = useState(0);

  // Use the stream hook to get real-time messages
  const { 
    data: messages, 
    isLoading, 
    error: streamError,
    cancel: cancelStream 
  } = useStream('stream.messages', [], {}, {
    maxItems: 100,
    onData: (chunk) => {
      // Auto-scroll on new message
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }
  });

  // Auto-scroll when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) {
      return;
    }

    try {
      setSendStatus('sending');
      
      // Send message to Piddy via RPC
      const result = await fetchApi('/api/messages/send', {
        method: 'POST',
        body: JSON.stringify({
          sender_id: 'user',
          receiver_id: 'Piddy',
          content: inputValue.trim(),
          priority: 2
        })
      });

      if (result.status === 'sent') {
        setSendStatus('sent');
        setInputValue('');
        setUserSendCount(userSendCount + 1);
        
        // Clear status after 2 seconds
        setTimeout(() => setSendStatus(''), 2000);
      } else {
        setSendStatus(`error: ${result.error || 'Failed to send'}`);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setSendStatus(`error: ${err.message}`);
    }
  };

  return (
    <div className="page live-chat-container">
      <h2>💬 Live Chat with Piddy</h2>
      
      {/* Status Bar */}
      <div className="live-chat-status">
        {isLoading && messages.length === 0 && (
          <span className="status-loading">🔄 Connecting...</span>
        )}
        {messages.length > 0 && (
          <span className="status-connected">🟢 Live ({messages.length} messages)</span>
        )}
        {streamError && (
          <span className="status-error">❌ {streamError}</span>
        )}
      </div>

      {/* Messages Container */}
      <div className="live-chat-messages">
        {messages.length === 0 && !isLoading && (
          <div className="no-messages">
            <p>No messages yet. Send one to get started!</p>
            <small>💡 Try: "what's happening" or "create mission"</small>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div 
            key={msg.id || idx} 
            className={`message ${msg.sender === 'user' ? 'user-message' : 'piddy-message'} ${msg.NEW ? 'new-message' : ''}`}
          >
            <div className="message-header">
              <span className="sender">{msg.sender}</span>
              <span className="timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
              {msg.priority > 1 && <span className="priority">⭐</span>}
            </div>
            <div className="message-content">{msg.content}</div>
            {msg.status === 'processing' && (
              <div className="message-status">⏳ Processing...</div>
            )}
            {msg.action && (
              <div className="message-action">→ {msg.action}</div>
            )}
          </div>
        ))}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="live-chat-input-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Talk to Piddy... e.g., 'what's happening' or 'create mission'"
          disabled={isLoading && messages.length === 0}
          className="live-chat-input"
        />
        <button 
          type="submit" 
          disabled={!inputValue.trim() || sendStatus === 'sending'}
          className="live-chat-send-btn"
        >
          {sendStatus === 'sending' ? '⏳' : '📤'} Send
        </button>
      </form>

      {/* Send Status */}
      {sendStatus && (
        <div className={`send-status ${sendStatus.startsWith('error') ? 'error' : 'success'}`}>
          {sendStatus}
        </div>
      )}

      {/* Help Text */}
      <div className="live-chat-help">
        <strong>💡 Tips:</strong>
        <ul>
          <li><code>"what's happening"</code> - See live agent activity</li>
          <li><code>"create mission: [description]"</code> - Start a new mission</li>
          <li><code>"execute: [task]"</code> - Run a task</li>
          <li><code>"status"</code> - System status</li>
          <li><code>"show agents"</code> - See all active agents</li>
        </ul>
      </div>
    </div>
  );
}

export default LiveChat;
