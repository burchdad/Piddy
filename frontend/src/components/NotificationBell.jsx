import React, { useState, useEffect, useRef } from 'react';
import { fetchApi } from '../utils/api';
import { useToast } from './Toast';
import '../styles/components.css';

function NotificationBell() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const panelRef = useRef(null);
  const prevUnreadRef = useRef(0);
  const toast = useToast();

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const data = await fetchApi('/api/notifications');
        setNotifications(data.notifications || []);
        const newUnread = data.unread_count || 0;

        // Show toast for new notifications
        if (newUnread > prevUnreadRef.current && prevUnreadRef.current >= 0) {
          const newest = (data.notifications || []).find(n => !n.read);
          if (newest) {
            const typeMap = { approval: 'success', rejection: 'warning', info: 'info', error: 'error' };
            const toastType = typeMap[newest.type] || 'info';
            toast[toastType](`🔔 ${newest.message}`);
          }
        }
        prevUnreadRef.current = newUnread;
        setUnreadCount(newUnread);
      } catch (err) {
        // silent fail on notification fetch
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 8000);
    return () => clearInterval(interval);
  }, []);

  // Close panel on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const markRead = async (id) => {
    try {
      await fetchApi('/api/notifications/mark_read', 'POST', { id });
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) { /* silent */ }
  };

  const markAllRead = async () => {
    try {
      await fetchApi('/api/notifications/read-all', 'POST');
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (err) { /* silent */ }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'approval': return '✅';
      case 'rejection': return '❌';
      case 'warning': return '⚠️';
      case 'error': return '🚨';
      default: return 'ℹ️';
    }
  };

  const timeAgo = (timestamp) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  };

  return (
    <div className="notification-bell-wrapper" ref={panelRef}>
      <button
        className={`notification-bell ${unreadCount > 0 ? 'has-unread' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title={`${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`}
      >
        🔔
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
        )}
      </button>

      {isOpen && (
        <div className="notification-panel">
          <div className="notification-panel-header">
            <h3>Notifications</h3>
            {unreadCount > 0 && (
              <button className="mark-all-read" onClick={markAllRead}>
                Mark all read
              </button>
            )}
          </div>
          <div className="notification-list">
            {notifications.length === 0 ? (
              <div className="notification-empty">
                <span>🔕</span>
                <p>No notifications yet</p>
              </div>
            ) : (
              notifications.slice(0, 20).map(n => (
                <div
                  key={n.id}
                  className={`notification-item ${n.read ? 'read' : 'unread'}`}
                  onClick={() => !n.read && markRead(n.id)}
                >
                  <span className="notification-icon">{getIcon(n.type)}</span>
                  <div className="notification-content">
                    <span className="notification-message">{n.message}</span>
                    <span className="notification-time">{timeAgo(n.timestamp)}</span>
                  </div>
                  {!n.read && <span className="notification-dot" />}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationBell;
