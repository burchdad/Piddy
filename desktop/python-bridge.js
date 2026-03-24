/**
 * Python Bridge - RPC Client for Electron
 * Handles request/response correlation, timeouts, and error handling
 * Replaces HTTP with direct function calls via stdio
 */

const StdioProtocol = require('./stdio-protocol');

const MESSAGE_TYPES = {
  REQUEST: 'request',
  RESPONSE: 'response',
  ERROR: 'error',
  STREAM_START: 'stream_start',
  STREAM_CHUNK: 'stream_chunk',
  STREAM_ERROR: 'stream_error',
  STREAM_END: 'stream_end',
  PING: 'ping',
  PONG: 'pong'
};

class PythonBridge {
  /**
   * Create a Python RPC bridge
   * @param {ChildProcess} pythonProcess - The spawned Python subprocess
   */
  constructor(pythonProcess) {
    this.pythonProcess = pythonProcess;
    this.protocol = new StdioProtocol(
      pythonProcess.stdin,
      pythonProcess.stdout,
      pythonProcess.stderr
    );
    
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.streamListeners = new Map();
    this.connected = false;
    this.maxRetries = 3;
    this.retryDelay = 1000; // ms
    
    // Setup message handler
    this.protocol.on('message', (msg) => {
      this._handleMessage(msg);
    });
    
    this.protocol.on('close', () => {
      console.log('[PythonBridge] Python process disconnected');
      this.connected = false;
    });
    
    this.protocol.on('error', (err) => {
      console.error('[PythonBridge] Protocol error:', err);
    });
    
    // Process exit handler
    this.pythonProcess.on('exit', (code, signal) => {
      console.log(`[PythonBridge] Python process exited: code=${code}, signal=${signal}`);
      this.connected = false;
    });
    
    // Test connection
    this._testConnection();
  }
  
  /**
   * Test connection to Python process
   * @private
   */
  async _testConnection() {
    // Retry ping with delay — Python backend needs time to import modules and start listening
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        // Wait for backend to initialize before first attempt
        if (attempt === 1) await new Promise(r => setTimeout(r, 3000));
        else await new Promise(r => setTimeout(r, 5000));
        
        console.log(`[PythonBridge] Connection test attempt ${attempt}/3...`);
        const result = await this.call('__ping__', [], {}, 15000);
        if (result && result.status === 'pong') {
          console.log('[PythonBridge] Connected to Python RPC server');
          this.connected = true;
          return;
        }
      } catch (err) {
        console.warn(`[PythonBridge] Connection test attempt ${attempt} failed:`, err.message);
      }
    }
    console.warn('[PythonBridge] All connection tests failed — RPC calls may still work');
  }
  
  /**
   * Call a Python function
   * @param {string} functionName - Name of function to call
   * @param {Array} args - Positional arguments
   * @param {Object} kwargs - Keyword arguments
   * @param {number} timeout - Call timeout in ms (default 30000)
   * @returns {Promise<any>} Function result
   */
  async call(functionName, args = [], kwargs = {}, timeout = 30000) {
    return new Promise((resolve, reject) => {
      const id = ++this.requestId;
      
      // Create timeout handler
      const timeoutHandle = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(
          `RPC timeout calling ${functionName} after ${timeout}ms`
        ));
      }, timeout);
      
      // Store request handler
      this.pendingRequests.set(id, {
        type: 'call',
        resolve: (result) => {
          clearTimeout(timeoutHandle);
          resolve(result);
        },
        reject: (error) => {
          clearTimeout(timeoutHandle);
          reject(error);
        }
      });
      
      // Send request
      try {
        const message = {
          type: MESSAGE_TYPES.REQUEST,
          id,
          function: functionName,
          args,
          kwargs
        };
        
        console.debug(`[RPC Call] ${functionName}(${JSON.stringify(args)}, ${JSON.stringify(kwargs)})`);
        this.protocol.send(message);
      } catch (err) {
        this.pendingRequests.delete(id);
        clearTimeout(timeoutHandle);
        reject(new Error(`Failed to send RPC request: ${err.message}`));
      }
    });
  }
  
  /**
   * Open a stream from Python
   * @param {string} functionName - Name of streaming function
   * @param {Array} args - Positional arguments
   * @param {Object} kwargs - Keyword arguments
   * @param {Function} onChunk - Callback for each chunk
   * @param {Function} onError - Error callback
   * @param {Function} onEnd - Completion callback
   * @param {number} timeout - Stream timeout (default 60000)
   * @returns {Function} Cleanup function
   */
  stream(functionName, args = [], kwargs = {}, onChunk, onError, onEnd, timeout = 60000) {
    const id = ++this.requestId;
    
    // Create timeout handler
    const timeoutHandle = setTimeout(() => {
      this.streamListeners.delete(id);
      onError?.(new Error(`Stream timeout after ${timeout}ms`));
    }, timeout);
    
    // Store stream handler
    this.streamListeners.set(id, {
      onChunk: (chunk) => {
        clearTimeout(timeoutHandle); // Reset timeout on each chunk
        const timeoutHandle2 = setTimeout(() => {
          this.streamListeners.delete(id);
          onError?.(new Error(`Stream timeout after ${timeout}ms`));
        }, timeout);
        onChunk?.(chunk);
      },
      onError: (error) => {
        clearTimeout(timeoutHandle);
        this.streamListeners.delete(id);
        onError?.(error);
      },
      onEnd: () => {
        clearTimeout(timeoutHandle);
        this.streamListeners.delete(id);
        onEnd?.();
      }
    });
    
    // Send streaming request
    try {
      const message = {
        type: MESSAGE_TYPES.REQUEST,
        id,
        function: functionName,
        args,
        kwargs
      };
      
      console.debug(`[RPC Stream] ${functionName}(${JSON.stringify(args)})`);
      this.protocol.send(message);
    } catch (err) {
      this.streamListeners.delete(id);
      clearTimeout(timeoutHandle);
      onError?.(new Error(`Failed to start stream: ${err.message}`));
    }
    
    // Return cleanup function
    return () => {
      clearTimeout(timeoutHandle);
      this.streamListeners.delete(id);
    };
  }
  
  /**
   * Handle message from Python
   * @private
   */
  _handleMessage(message) {
    const { type, id } = message;
    
    // Handle regular RPC response
    if (type === MESSAGE_TYPES.RESPONSE) {
      const handler = this.pendingRequests.get(id);
      if (handler) {
        this.pendingRequests.delete(id);
        console.debug(`[RPC Response] id=${id}:`, message.result);
        handler.resolve(message.result);
      }
    }
    
    // Handle RPC error
    else if (type === MESSAGE_TYPES.ERROR) {
      const handler = this.pendingRequests.get(id);
      if (handler) {
        this.pendingRequests.delete(id);
        const error = new Error(message.error);
        if (message.error_traceback) {
          error.traceback = message.error_traceback;
        }
        console.debug(`[RPC Error] id=${id}:`, message.error);
        handler.reject(error);
      }
    }
    
    // Handle stream start
    else if (type === MESSAGE_TYPES.STREAM_START) {
      const handler = this.streamListeners.get(id);
      if (handler) {
        console.debug(`[RPC Stream Start] id=${id}`);
      }
    }
    
    // Handle stream chunk
    else if (type === MESSAGE_TYPES.STREAM_CHUNK) {
      const handler = this.streamListeners.get(id);
      if (handler) {
        console.debug(`[RPC Stream Chunk] id=${id}, seq=${message.sequence}:`, message.result);
        handler.onChunk(message.result);
      }
    }
    
    // Handle stream error
    else if (type === MESSAGE_TYPES.STREAM_ERROR) {
      const handler = this.streamListeners.get(id);
      if (handler) {
        this.streamListeners.delete(id);
        const error = new Error(message.error);
        if (message.error_traceback) {
          error.traceback = message.error_traceback;
        }
        console.error(`[RPC Stream Error] id=${id}:`, message.error);
        handler.onError(error);
      }
    }
    
    // Handle stream end
    else if (type === MESSAGE_TYPES.STREAM_END) {
      const handler = this.streamListeners.get(id);
      if (handler) {
        console.debug(`[RPC Stream End] id=${id}, total sequences=${message.sequence}`);
        handler.onEnd();
      }
    }
    
    // Handle pong (connection test)
    else if (type === MESSAGE_TYPES.PONG) {
      console.debug(`[RPC Pong] id=${id}`);
    }
  }
  
  /**
   * Close the bridge
   */
  close() {
    try {
      this.protocol.close();
    } catch (err) {
      console.error('[PythonBridge] Error closing:', err);
    }
  }
  
  /**
   * Check if connected
   */
  isConnected() {
    return this.connected;
  }
}

module.exports = PythonBridge;
