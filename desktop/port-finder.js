/**
 * Dynamic Port Assignment Utility
 * Finds available ports at runtime for zero-conflict deployment
 */

const net = require('net');

/**
 * Find an available port starting from a base port
 * @param {number} basePort - Starting port to check
 * @param {number} maxAttempts - Maximum ports to check
 * @returns {Promise<number>} Available port number
 */
async function findAvailablePort(basePort = 8000, maxAttempts = 20) {
  for (let i = 0; i < maxAttempts; i++) {
    const port = basePort + i;
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available ports found between ${basePort} and ${basePort + maxAttempts}`);
}

/**
 * Check if a port is available
 * @param {number} port - Port to check
 * @returns {Promise<boolean>} True if port is available
 */
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    
    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(false);
      } else {
        resolve(false);
      }
    });
    
    server.once('listening', () => {
      server.close();
      resolve(true);
    });
    
    server.listen(port, '127.0.0.1');
  });
}

/**
 * Get a port with validation
 * @param {number} preferredPort - Preferred port
 * @param {number} fallbackPort - Fallback base port
 * @returns {Promise<number>} Available port
 */
async function getPort(preferredPort = 8000, fallbackPort = 8080) {
  // Try preferred port first
  if (await isPortAvailable(preferredPort)) {
    return preferredPort;
  }
  
  // Fallback to finding available port
  return findAvailablePort(fallbackPort);
}

module.exports = {
  findAvailablePort,
  isPortAvailable,
  getPort
};
