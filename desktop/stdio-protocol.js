/**
 * Stdio Protocol - Message framing for Node <-> Python RPC communication
 * Handles JSON message serialization/deserialization over process stdin/stdout
 */

const { EventEmitter } = require('events');
const readline = require('readline');

class StdioProtocol extends EventEmitter {
  /**
   * Create a stdio protocol handler
   * @param {Stream} stdin - Process stdin (write to Python)
   * @param {Stream} stdout - Process stdout (read from Python)
   * @param {Stream} stderr - Process stderr (for logging)
   */
  constructor(stdin, stdout, stderr = null) {
    super();
    
    this.stdin = stdin;
    this.stdout = stdout;
    this.stderr = stderr;
    
    this.messageHandlers = [];
    this.lineBuffer = '';
    
    // Setup readline for line-by-line parsing
    this.rl = readline.createInterface({
      input: stdout,
      output: undefined, // Don't write back
      terminal: false,
      crlfDelay: Infinity
    });
    
    // Listen for lines (each RPC message is one line of JSON)
    this.rl.on('line', (line) => {
      this._handleLine(line);
    });
    
    this.rl.on('close', () => {
      this.emit('close');
    });
    
    this.rl.on('error', (err) => {
      this.emit('error', err);
    });
    
    // Log stderr if provided
    if (stderr) {
      const stderrRL = readline.createInterface({
        input: stderr,
        output: undefined,
        terminal: false
      });
      
      stderrRL.on('line', (line) => {
        if (line.includes('[RPC]')) {
          // Log RPC server messages
          console.log('[Python RPC]', line);
        } else if (line) {
          console.log('[Python]', line);
        }
      });
    }
  }
  
  /**
   * Send a message to Python
   * @param {Object} message - Message object to send
   */
  send(message) {
    try {
      const json = JSON.stringify(message);
      this.stdin.write(json + '\n');
    } catch (err) {
      this.emit('error', new Error(`Failed to send message: ${err.message}`));
    }
  }
  
  /**
   * Handle incoming line from Python
   * @private
   */
  _handleLine(line) {
    if (!line || line.trim() === '') {
      return;
    }
    
    try {
      const message = JSON.parse(line);
      this.emit('message', message);
    } catch (err) {
      console.error('[Stdio Protocol] Failed to parse JSON:', line);
      this.emit('error', new Error(`JSON parse error: ${err.message}`));
    }
  }
  
  /**
   * Gracefully close the protocol
   */
  close() {
    try {
      this.rl.close();
      if (this.stdin.destroy) {
        this.stdin.destroy();
      }
    } catch (err) {
      console.error('[Stdio Protocol] Error closing:', err);
    }
  }
}

module.exports = StdioProtocol;
