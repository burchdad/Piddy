import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useStream } from '../hooks/useStream';
import { apiCall } from '../utils/api';
import '../styles/components.css';

/**
 * Detect whether Electron streaming is available.
 * Primary mode = Electron stream via window.piddy.streamManager
 * Fallback = HTTP /api/chat for browser dev mode
 */
const hasElectronStream = () =>
  !!(window.piddy?.streamManager || (typeof global !== 'undefined' && global.streamManager));

/**
 * LiveChat - Real-time conversation with Piddy
 *
 * Electron (primary):  Uses useStream('stream.messages') for live push data
 *                      and fetchApi RPC for sending.
 * Browser (fallback):  Uses HTTP POST /api/chat for request/response.
 */
function LiveChat() {
  const [inputValue, setInputValue] = useState('');
  const [sendStatus, setSendStatus] = useState('');
  const messagesEndRef = useRef(null);
  const isElectron = hasElectronStream();

  // ── Electron stream state ──────────────────────────────────────────
  const {
    data: streamMessages,
    isLoading,
    error: streamError,
  } = useStream('stream.messages', [], {}, {
    maxItems: 100,
    autoStart: isElectron, // only auto-start when Electron is present
    onData: () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    },
  });

  // ── HTTP fallback state (browser dev mode) ─────────────────────────
  const [httpMessages, setHttpMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  // Unified message list — Electron stream takes priority
  const messages = isElectron ? streamMessages : httpMessages;

  // Auto-scroll on message change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  // ── Send handler (works in both modes) ─────────────────────────────
  const handleSendMessage = useCallback(async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    const text = inputValue.trim();

    if (isElectron) {
      // ── Electron path: RPC send via api bridge ───────────────────
      try {
        setSendStatus('sending');
        const result = await apiCall('/api/messages/send', {
          method: 'POST',
          data: {
            sender_id: 'user',
            receiver_id: 'Piddy',
            content: text,
            priority: 2,
          },
        });

        if (result.status === 'sent') {
          setSendStatus('');
          setInputValue('');
        } else {
          setSendStatus(`error: ${result.error || 'Failed to send'}`);
        }
      } catch (err) {
        console.error('Error sending message:', err);
        setSendStatus(`error: ${err.message}`);
      }
    } else {
      // ── HTTP fallback path: request/response via /api/chat ───────
      const userMsg = {
        id: Date.now(),
        sender: 'user',
        content: text,
        timestamp: new Date().toISOString(),
      };
      setHttpMessages((prev) => [...prev, userMsg]);
      setInputValue('');

      try {
        setSendStatus('sending');
        const result = await apiCall('/api/chat', {
          method: 'POST',
          data: { message: text, session_id: sessionId },
        });

        if (result.session_id) setSessionId(result.session_id);

        setHttpMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'Piddy',
            content: result.reply || result.error || 'No response',
            timestamp: new Date().toISOString(),
            source: result.source,
          },
        ]);
        setSendStatus('');
      } catch (err) {
        console.error('Error sending message:', err);
        setSendStatus(`error: ${err.message}`);
        setHttpMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'Piddy',
            content: `Error: ${err.message}`,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    }
  }, [inputValue, isElectron, sessionId]);

  return (
    <div className="page live-chat-container">
      <h2>💬 Live Chat with Piddy</h2>

      {/* Status Bar */}
      <div className="live-chat-status">
        {isElectron && isLoading && messages.length === 0 && (
          <span className="status-loading">🔄 Connecting...</span>
        )}
        {isElectron && messages.length > 0 && (
          <span className="status-connected">🟢 Live ({messages.length} messages)</span>
        )}
        {isElectron && streamError && (
          <span className="status-error">❌ {streamError}</span>
        )}
        {!isElectron && (
          <span className="status-connected">🌐 Browser mode — HTTP chat</span>
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
              {msg.source && <span className="source-badge">{msg.source}</span>}
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

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="live-chat-input-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Talk to Piddy... e.g., 'what's happening' or 'create mission'"
          disabled={isElectron && isLoading && messages.length === 0}
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
      {sendStatus && sendStatus.startsWith('error') && (
        <div className="send-status error">{sendStatus}</div>
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
