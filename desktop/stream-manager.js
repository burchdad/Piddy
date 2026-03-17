/**
 * IPC Streaming Protocol - Real-time Updates
 * 
 * Handles streaming data from Python backend to Electron frontend.
 * Enables live logs, agent thoughts, metrics, and progress updates.
 * 
 * Protocol:
 * - Client requests stream with unique stream ID
 * - Server sends chunks as they become available
 * - Each chunk has sequence number for ordering
 * - Stream ends with explicit end marker
 * - Backpressure handled via pause/resume
 */

const { EventEmitter } = require('events');

class StreamHandler extends EventEmitter {
  constructor(streamId, pythonBridge) {
    super();
    this.streamId = streamId;
    this.pythonBridge = pythonBridge;
    this.isActive = true;
    this.paused = false;
    this.queue = [];
    this.lastSequence = -1;
    
    // Bind methods
    this.on('chunk', (data) => this._handleChunk(data));
    this.on('end', () => this._handleEnd());
    this.on('error', (err) => this._handleError(err));
  }
  
  _handleChunk(data) {
    if (!this.isActive) return;
    
    // Check sequence order
    if (data.sequence > this.lastSequence + 1) {
      console.warn(`[STREAM] Out of order chunk: expected ${this.lastSequence + 1}, got ${data.sequence}`);
    }
    this.lastSequence = data.sequence;
    
    // Handle backpressure
    if (this.paused) {
      this.queue.push(data);
    } else {
      this.emit('data', data);
    }
  }
  
  _handleEnd() {
    this.isActive = false;
    this.queue = [];
    this.emit('complete');
  }
  
  _handleError(err) {
    this.isActive = false;
    this.queue = [];
    this.emit('error', err);
  }
  
  pause() {
    this.paused = true;
  }
  
  resume() {
    this.paused = false;
    
    // Flush queue
    while (this.queue.length > 0 && !this.paused) {
      const data = this.queue.shift();
      this.emit('data', data);
    }
  }
  
  cancel() {
    this.isActive = false;
    this.queue = [];
    this.emit('cancelled');
  }
}

class StreamManager extends EventEmitter {
  constructor(pythonBridge) {
    super();
    this.pythonBridge = pythonBridge;
    this.streams = new Map();
    this.nextStreamId = 1;
  }
  
  /**
   * Start a new stream
   * @param {string} functionName - RPC function name
   * @param {Array} args - Function arguments
   * @param {Object} kwargs - Keyword arguments
   * @returns {StreamHandler} Stream handler for receiving chunks
   */
  startStream(functionName, args = [], kwargs = {}) {
    const streamId = this.nextStreamId++;
    const handler = new StreamHandler(streamId, this.pythonBridge);
    
    this.streams.set(streamId, handler);
    
    // Setup Python streaming call
    this.pythonBridge.stream(
      functionName,
      args,
      kwargs,
      (chunk) => {
        // On each chunk
        handler.emit('chunk', chunk);
      },
      (error) => {
        // On stream error
        handler.emit('error', error);
        this.streams.delete(streamId);
      },
      () => {
        // On stream end
        handler.emit('end');
        this.streams.delete(streamId);
      }
    );
    
    return handler;
  }
  
  /**
   * Helper: Stream system logs
   * @param {function} onLog - Callback for each log line
   * @returns {StreamHandler}
   */
  streamLogs(onLog) {
    const stream = this.startStream('stream.logs', [], {});
    stream.on('data', (data) => {
      if (data.message) {
        onLog({
          timestamp: data.timestamp || new Date().toISOString(),
          level: data.level || 'INFO',
          message: data.message,
          source: data.source || 'System'
        });
      }
    });
    return stream;
  }
  
  /**
   * Helper: Stream agent thoughts/decisions
   * @param {function} onThought - Callback for each thought
   * @returns {StreamHandler}
   */
  streamAgentThoughts(agentId, onThought) {
    const stream = this.startStream('stream.agent_thoughts', [agentId], {});
    stream.on('data', (data) => {
      if (data.thought) {
        onThought({
          agent_id: agentId,
          timestamp: data.timestamp || new Date().toISOString(),
          thought: data.thought,
          reasoning: data.reasoning,
          confidence: data.confidence || 0.5
        });
      }
    });
    return stream;
  }
  
  /**
   * Helper: Stream mission progress
   * @param {string} missionId - Mission ID to stream
   * @param {function} onProgress - Callback for progress updates
   * @returns {StreamHandler}
   */
  streamMissionProgress(missionId, onProgress) {
    const stream = this.startStream('stream.mission_progress', [missionId], {});
    stream.on('data', (data) => {
      onProgress({
        mission_id: missionId,
        phase: data.phase,
        progress_percent: data.progress_percent || 0,
        current_step: data.current_step,
        status: data.status,
        timestamp: data.timestamp || new Date().toISOString()
      });
    });
    return stream;
  }
  
  /**
   * Helper: Stream system metrics (CPU, memory, etc.)
   * @param {function} onMetrics - Callback for metrics update
   * @returns {StreamHandler}
   */
  streamSystemMetrics(onMetrics) {
    const stream = this.startStream('stream.system_metrics', [], {});
    stream.on('data', (data) => {
      onMetrics({
        cpu_percent: data.cpu_percent || 0,
        memory_mb: data.memory_mb || 0,
        memory_percent: data.memory_percent || 0,
        disk_percent: data.disk_percent || 0,
        timestamp: data.timestamp || new Date().toISOString()
      });
    });
    return stream;
  }
  
  /**
   * List all active streams
   * @returns {Array} Stream IDs and their handlers
   */
  getActiveStreams() {
    return Array.from(this.streams.entries()).map(([id, handler]) => ({
      id,
      isActive: handler.isActive,
      isPaused: handler.paused
    }));
  }
  
  /**
   * Stop all streams
   */
  stopAllStreams() {
    for (const [, handler] of this.streams) {
      handler.cancel();
    }
    this.streams.clear();
  }
}

module.exports = { StreamHandler, StreamManager };
