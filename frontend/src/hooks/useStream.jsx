/**
 * useStream - React Hook for Real-time Streaming Data
 * 
 * Usage:
 *   const { data, isLoading, error, pause, resume, cancel } = useStream('stream.logs', []);
 *   
 *   data will be an array that updates as chunks arrive
 *   Each chunk is appended to the array
 */

import { useEffect, useState, useCallback, useRef } from 'react';

/**
 * Hook for consuming streaming data from RPC backend
 * 
 * @param {string} streamName - Name of stream function (e.g., 'stream.logs')
 * @param {Array} args - Arguments for stream function
 * @param {Object} kwargs - Keyword arguments for stream function
 * @param {Object} options - Hook options (maxItems, onData, onError, onEnd)
 * @returns {Object} { data, isLoading, error, pause, resume, cancel, stream }
 */
export function useStream(streamName, args = [], kwargs = {}, options = {}) {
  const {
    maxItems = 1000,  // Keep only last N items
    onData = null,    // Callback on each chunk
    onError = null,   // Callback on error
    onEnd = null,     // Callback when stream ends
    autoStart = true  // Auto-start stream on mount
  } = options;

  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(autoStart);
  const [error, setError] = useState(null);
  const streamHandlerRef = useRef(null);

  // Start stream
  const start = useCallback(() => {
    if (streamHandlerRef.current && streamHandlerRef.current.isActive) {
      console.warn('[useStream] Stream already active');
      return;
    }

    setIsLoading(true);
    setError(null);
    setData([]);

    try {
      // Get stream manager from main Electron process
      const streamManager = window.piddy?.streamManager || (typeof global !== 'undefined' && global.streamManager);
      if (!streamManager) {
        // Not in Electron — silently degrade (no error banner)
        console.info('[useStream] No streamManager — running in browser mode');
        setIsLoading(false);
        return;
      }

      const handler = streamManager.startStream(streamName, args, kwargs);
      streamHandlerRef.current = handler;

      // Handle data chunks
      handler.on('data', (chunk) => {
        setData((prevData) => {
          const newData = [...prevData, chunk];
          // Keep only last maxItems
          if (newData.length > maxItems) {
            return newData.slice(-maxItems);
          }
          return newData;
        });

        if (onData) {
          onData(chunk);
        }
      });

      // Handle errors
      handler.on('error', (err) => {
        console.error(`[useStream] Stream error: ${err}`);
        setError(err.toString());
        setIsLoading(false);

        if (onError) {
          onError(err);
        }
      });

      // Handle stream end
      handler.on('complete', () => {
        setIsLoading(false);

        if (onEnd) {
          onEnd();
        }
      });

      // Handle cancellation
      handler.on('cancelled', () => {
        setIsLoading(false);
      });

    } catch (err) {
      console.error('[useStream] Failed to start stream:', err);
      setError(err.message);
      setIsLoading(false);
    }
  }, [streamName, args, kwargs, maxItems, onData, onError, onEnd]);

  // Pause stream
  const pause = useCallback(() => {
    if (streamHandlerRef.current) {
      streamHandlerRef.current.pause();
    }
  }, []);

  // Resume stream
  const resume = useCallback(() => {
    if (streamHandlerRef.current) {
      streamHandlerRef.current.resume();
    }
  }, []);

  // Cancel stream
  const cancel = useCallback(() => {
    if (streamHandlerRef.current) {
      streamHandlerRef.current.cancel();
      streamHandlerRef.current = null;
    }
    setIsLoading(false);
  }, []);

  // Auto-start on mount
  useEffect(() => {
    if (autoStart) {
      start();
    }

    return () => {
      // Cleanup: cancel stream on unmount
      cancel();
    };
  }, [autoStart, start, cancel]);

  return {
    data,
    isLoading,
    error,
    pause,
    resume,
    cancel,
    restart: start,
    stream: streamHandlerRef.current
  };
}

/**
 * Hook for streaming system logs
 */
export function useStreamLogs(options = {}) {
  return useStream('stream.logs', [], {}, {
    maxItems: 500,
    ...options
  });
}

/**
 * Hook for streaming agent thoughts
 */
export function useStreamAgentThoughts(agentId, options = {}) {
  return useStream('stream.agent_thoughts', [agentId], {}, {
    maxItems: 200,
    ...options
  });
}

/**
 * Hook for streaming mission progress
 */
export function useStreamMissionProgress(missionId, options = {}) {
  return useStream('stream.mission_progress', [missionId], {}, {
    maxItems: 100,
    ...options
  });
}

/**
 * Hook for streaming system metrics
 */
export function useStreamSystemMetrics(options = {}) {
  return useStream('stream.system_metrics', [], {}, {
    maxItems: 60,  // Keep last 60 seconds of metrics
    ...options
  });
}

/**
 * Example component using streaming hooks
 */
export function StreamingLogsViewer() {
  const { data, isLoading, error, cancel } = useStreamLogs();

  if (error) {
    return (
      <div style={{ padding: '1rem', color: 'red' }}>
        Stream Error: {error}
        <button onClick={cancel}>Close</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '1rem', fontFamily: 'monospace' }}>
      <h3>Live Logs {isLoading && '(streaming...)'}</h3>
      <div style={{
        height: '400px',
        overflow: 'auto',
        backgroundColor: '#1e1e1e',
        color: '#00ff00',
        padding: '1rem'
      }}>
        {data.map((entry, idx) => (
          <div key={idx} style={{ marginBottom: '0.5rem' }}>
            <span style={{ color: entry.level === 'ERROR' ? '#ff0000' : '#00ff00' }}>
              [{entry.level}]
            </span>
            {' '}
            <span style={{ color: '#888' }}>{entry.timestamp}</span>
            {' '}
            {entry.message}
          </div>
        ))}
      </div>
    </div>
  );
}

export default useStream;
