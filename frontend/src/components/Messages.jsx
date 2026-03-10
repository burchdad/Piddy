import React, { useEffect, useState } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function Messages() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetchApi('/api/messages')
      .then(data => setMessages(Array.isArray(data) ? data : (data.messages || [])))
      .catch(e => console.error(e));
  }, []);

  return (
    <div className="page">
      <h2>Messages</h2>
      {messages.length > 0 ? (
        <div style={{ padding: '20px' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ padding: '10px', borderBottom: '1px solid #ccc', marginBottom: '10px' }}>
              <strong>{msg.agent}</strong>: {msg.text}
            </div>
          ))}
        </div>
      ) : (
        <p>No messages</p>
      )}
    </div>
  );
}

export default Messages;
