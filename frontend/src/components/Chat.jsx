import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useStream } from '../hooks/useStream';
import { apiCall } from '../utils/api';
import PiddyAvatar from './PiddyAvatar';

/**
 * Unified Chat — Electron stream (primary) with HTTP fallback (browser dev).
 * Merges the old Chat + LiveChat into a single component.
 */
const hasElectronStream = () =>
  !!(window.piddy?.streamManager || (typeof global !== 'undefined' && global.streamManager));

function Chat({ onOpenSessions, onFilesCreated }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const isElectron = hasElectronStream();

  // ── Electron stream (when running in desktop app) ──────────────────
  const {
    data: streamMessages,
    isLoading: streamLoading,
    error: streamError,
  } = useStream('stream.messages', [], {}, {
    maxItems: 100,
    autoStart: isElectron,
    onData: () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    },
  });

  // In Electron mode, merge stream messages into our messages array
  useEffect(() => {
    if (!isElectron || !streamMessages?.length) return;
    const mapped = streamMessages.map(m => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.content,
      source: m.source,
      timestamp: m.timestamp || new Date().toISOString(),
    }));
    setMessages(mapped);
  }, [isElectron, streamMessages]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);
  useEffect(() => { inputRef.current?.focus(); }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isTyping) return;

    const userMsg = { role: 'user', content: text, timestamp: new Date().toISOString() };

    if (isElectron) {
      // Electron: send via chat RPC for full AI + file actions support
      setMessages(prev => [...prev, userMsg]);
      setInput('');
      setIsTyping(true);
      setError(null);
      try {
        const data = await apiCall('/api/chat', {
          method: 'POST',
          data: { message: text, session_id: sessionId },
          timeout: 120000,
        });
        if (data.error) { setError(data.error); setIsTyping(false); return; }
        if (data.session_id) setSessionId(data.session_id);

        const actions = data.actions || null;
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.reply,
          source: data.source,
          actions,
          timestamp: new Date().toISOString(),
        }]);

        if (actions && actions.length > 0 && onFilesCreated) {
          onFilesCreated(actions);
        }
      } catch (err) {
        setError(`Send failed: ${err.message}`);
      } finally {
        setIsTyping(false);
      }
    } else {
      // Browser: HTTP request/response
      setMessages(prev => [...prev, userMsg]);
      setInput('');
      setIsTyping(true);
      setError(null);

      try {
        const data = await apiCall('/api/chat', {
          method: 'POST',
          data: { message: text, session_id: sessionId },
          timeout: 120000,
        });

        if (data.error) { setError(data.error); setIsTyping(false); return; }
        if (data.session_id) setSessionId(data.session_id);

        const actions = data.actions || null;
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.reply,
          source: data.source,
          actions,
          timestamp: new Date().toISOString(),
        }]);

        // Open files in code panel when Piddy creates them
        if (actions && actions.length > 0 && onFilesCreated) {
          onFilesCreated(actions);
        }
      } catch (err) {
        setError('Failed to reach Piddy. Is the backend running?');
      } finally {
        setIsTyping(false);
      }
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setError(null);
    inputRef.current?.focus();
  };

  // Load a session from history
  const loadSession = useCallback(async (sid) => {
    try {
      const data = await apiCall(`/api/sessions/${sid}`);
      if (data.error) return;
      setSessionId(sid);
      setMessages(
        (data.messages || []).map(m => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp,
        }))
      );
    } catch {
      // ignore
    }
  }, []);

  // Expose loadSession for parent use
  useEffect(() => {
    if (window.__piddyChat) return;
    window.__piddyChat = { loadSession };
    return () => { delete window.__piddyChat; };
  }, [loadSession]);

  return (
    <div className="chat-page">
      {/* Toolbar */}
      <div className="chat-toolbar">
        <div className="chat-toolbar-left">
          <PiddyAvatar size="sm" />
          <h2 className="chat-title">Chat with Piddy</h2>
          {isElectron && <span className="chat-mode-badge live">Live</span>}
          {sessionId && <span className="chat-session-badge">Session active</span>}
        </div>
        <div className="chat-toolbar-right">
          {onOpenSessions && (
            <button className="chat-btn-secondary" onClick={onOpenSessions}>History</button>
          )}
          <button className="chat-btn-secondary" onClick={startNewChat}>+ New Chat</button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 && !isTyping && (
          <div className="chat-empty">
            <div className="chat-empty-icon">🎯</div>
            <h3>What can I help you with?</h3>
            <p>I can help you build, debug, and manage your projects.</p>
            <div className="chat-suggestions">
              {['What can you do?', 'Check system health', 'Show my skills', 'Help me build an API'].map(s => (
                <button key={s} className="chat-suggestion" onClick={() => { setInput(s); inputRef.current?.focus(); }}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <div className="chat-bubble-avatar">
              {msg.role === 'user' ? '👤' : '🎯'}
            </div>
            <div className="chat-bubble-body">
              <div className="chat-bubble-header">
                <span className="chat-bubble-sender">{msg.role === 'user' ? 'You' : 'Piddy'}</span>
                {msg.source && <span className="chat-bubble-source">{msg.source}</span>}
                <span className="chat-bubble-time">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className="chat-bubble-content">
                {msg.content.split('\n').map((line, j) => (
                  <React.Fragment key={j}>{line}<br /></React.Fragment>
                ))}
              </div>
              {msg.actions && msg.actions.length > 0 && (
                <div className="chat-actions-panel">
                  <div className="chat-actions-header">
                    <span className="chat-actions-icon">🛠️</span>
                    <span>Files created ({msg.actions.filter(a => a.success).length}/{msg.actions.length})</span>
                  </div>
                  <ul className="chat-actions-list">
                    {msg.actions.map((action, k) => (
                      <li key={k} className={`chat-action-item ${action.success ? 'success' : 'error'}`}>
                        <span className="chat-action-status">{action.success ? '✅' : '❌'}</span>
                        <span className="chat-action-path">{action.path}</span>
                        {action.size && <span className="chat-action-size">{action.size}B</span>}
                        {action.error && <span className="chat-action-error">{action.error}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="chat-bubble assistant">
            <div className="chat-bubble-avatar">🎯</div>
            <div className="chat-bubble-body">
              <div className="chat-typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}

        {(error || streamError) && (
          <div className="chat-error">
            <span>⚠️</span> {error || streamError}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="chat-input-bar">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(e); } }}
          onPaste={e => {
            const items = e.clipboardData?.items;
            if (!items) return;
            for (const item of items) {
              if (item.type.startsWith('image/')) {
                e.preventDefault();
                const file = item.getAsFile();
                const reader = new FileReader();
                reader.onload = () => setInput(prev => prev + `[Image: ${file.name || 'screenshot.png'}]`);
                reader.readAsDataURL(file);
                return;
              }
            }
          }}
          placeholder="Ask Piddy anything... (Shift+Enter for new line)"
          disabled={isTyping}
          className="chat-input"
          rows={1}
        />
        <button type="submit" disabled={!input.trim() || isTyping} className="chat-send-btn">
          {isTyping ? (
            <span className="chat-send-spinner" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13" /><path d="M22 2L15 22L11 13L2 9L22 2Z" />
            </svg>
          )}
        </button>
      </form>
    </div>
  );
}

export default Chat;
