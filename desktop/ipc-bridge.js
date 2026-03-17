/**
 * IPC Bridge for API Communication
 * Replaces HTTP calls with Electron IPC for zero-port architecture
 * 
 * Usage in frontend:
 *   const data = await window.piddy.api.system.overview();
 *   const result = await window.piddy.api.agents.create({name: 'Bot'});
 */

const { ipcMain } = require('electron');

// Setup IPC handlers for all backend APIs
function setupIPCBridge() {
  console.log('[IPC Bridge] Initializing API handlers...');
  
  /**
   * System Endpoints
   */
  ipcMain.handle('api:system:overview', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system/overview');
      return await response.json();
    } catch (err) {
      console.error('[IPC] system:overview failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:health', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system/health');
      return await response.json();
    } catch (err) {
      console.error('[IPC] system:health failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:config', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system/config');
      return await response.json();
    } catch (err) {
      console.error('[IPC] system:config failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:metrics', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system/metrics');
      return await response.json();
    } catch (err) {
      console.error('[IPC] system:metrics failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:logs', async (event, filters) => {
    try {
      const response = await fetch('http://localhost:8000/api/system/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] system:logs failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:status', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system/status');
      return await response.json();
    } catch (err) {
      console.error('[IPC] system:status failed:', err.message);
      throw err;
    }
  });

  /**
   * Agent Endpoints
   */
  ipcMain.handle('api:agents:list', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents');
      return await response.json();
    } catch (err) {
      console.error('[IPC] agents:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:get', async (event, agentId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/agents/${agentId}`);
      return await response.json();
    } catch (err) {
      console.error('[IPC] agents:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:create', async (event, config) => {
    try {
      const response = await fetch('http://localhost:8000/api/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] agents:create failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:update', async (event, agentId, config) => {
    try {
      const response = await fetch(`http://localhost:8000/api/agents/${agentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] agents:update failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:delete', async (event, agentId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/agents/${agentId}`, {
        method: 'DELETE'
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] agents:delete failed:', err.message);
      throw err;
    }
  });

  /**
   * Message Endpoints
   */
  ipcMain.handle('api:messages:list', async (event, filters) => {
    try {
      const response = await fetch('http://localhost:8000/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] messages:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:messages:get', async (event, messageId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/messages/${messageId}`);
      return await response.json();
    } catch (err) {
      console.error('[IPC] messages:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:messages:send', async (event, message) => {
    try {
      const response = await fetch('http://localhost:8000/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] messages:send failed:', err.message);
      throw err;
    }
  });

  /**
   * Decision Endpoints
   */
  ipcMain.handle('api:decisions:list', async (event, filters) => {
    try {
      const response = await fetch('http://localhost:8000/api/decisions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] decisions:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:decisions:get', async (event, decisionId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/decisions/${decisionId}`);
      return await response.json();
    } catch (err) {
      console.error('[IPC] decisions:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:decisions:create', async (event, decision) => {
    try {
      const response = await fetch('http://localhost:8000/api/decisions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(decision)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] decisions:create failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:decisions:update', async (event, decisionId, decision) => {
    try {
      const response = await fetch(`http://localhost:8000/api/decisions/${decisionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(decision)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] decisions:update failed:', err.message);
      throw err;
    }
  });

  /**
   * Mission Endpoints
   */
  ipcMain.handle('api:missions:list', async (event, filters) => {
    try {
      const response = await fetch('http://localhost:8000/api/missions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] missions:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:get', async (event, missionId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/missions/${missionId}`);
      return await response.json();
    } catch (err) {
      console.error('[IPC] missions:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:create', async (event, mission) => {
    try {
      const response = await fetch('http://localhost:8000/api/missions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mission)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] missions:create failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:update', async (event, missionId, mission) => {
    try {
      const response = await fetch(`http://localhost:8000/api/missions/${missionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mission)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] missions:update failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:execute', async (event, missionId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/missions/${missionId}/execute`, {
        method: 'POST'
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] missions:execute failed:', err.message);
      throw err;
    }
  });

  /**
   * Generic GET/POST handlers for flexibility
   */
  ipcMain.handle('api:get', async (event, endpoint, queryParams) => {
    try {
      let url = `http://localhost:8000${endpoint}`;
      if (queryParams && Object.keys(queryParams).length > 0) {
        const qs = new URLSearchParams(queryParams).toString();
        url += `?${qs}`;
      }
      const response = await fetch(url);
      return await response.json();
    } catch (err) {
      console.error('[IPC] generic GET failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:post', async (event, endpoint, data) => {
    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] generic POST failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:put', async (event, endpoint, data) => {
    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] generic PUT failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:delete', async (event, endpoint) => {
    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'DELETE'
      });
      return await response.json();
    } catch (err) {
      console.error('[IPC] generic DELETE failed:', err.message);
      throw err;
    }
  });

  console.log('[IPC Bridge] All API handlers registered successfully');
}

module.exports = setupIPCBridge;
    try {
      const response = await fetch('http://localhost:8000/api/messages');
      return await response.json();
    } catch (err) {
      logger.error(`IPC messages:list failed: ${err.message}`);
      throw err;
    }
  });

  // Get Decisions
  ipcMain.handle('api:decisions:list', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/decisions');
      return await response.json();
    } catch (err) {
      logger.error(`IPC decisions:list failed: ${err.message}`);
      throw err;
    }
  });

  // Get Missions
  ipcMain.handle('api:missions:list', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/missions');
      return await response.json();
    } catch (err) {
      logger.error(`IPC missions:list failed: ${err.message}`);
      throw err;
    }
  });

  // Get Logs
  ipcMain.handle('api:logs:list', async (event, options = {}) => {
    try {
      const params = new URLSearchParams(options);
      const response = await fetch(`http://localhost:8000/api/logs?${params}`);
      return await response.json();
    } catch (err) {
      logger.error(`IPC logs:list failed: ${err.message}`);
      throw err;
    }
  });

  // Get Tests
  ipcMain.handle('api:tests:summary', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/tests/summary');
      return await response.json();
    } catch (err) {
      logger.error(`IPC tests:summary failed: ${err.message}`);
      throw err;
    }
  });

  ipcMain.handle('api:tests:list', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/tests');
      return await response.json();
    } catch (err) {
      logger.error(`IPC tests:list failed: ${err.message}`);
      throw err;
    }
  });

  // Get Metrics
  ipcMain.handle('api:metrics:performance', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/metrics/performance');
      return await response.json();
    } catch (err) {
      logger.error(`IPC metrics:performance failed: ${err.message}`);
      throw err;
    }
  });

  // Get Phases
  ipcMain.handle('api:phases:list', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/phases');
      return await response.json();
    } catch (err) {
      logger.error(`IPC phases:list failed: ${err.message}`);
      throw err;
    }
  });

  // Get Security Audit
  ipcMain.handle('api:security:audit', async () => {
    try {
      const response = await fetch('http://localhost:8000/api/security/audit');
      return await response.json();
    } catch (err) {
      logger.error(`IPC security:audit failed: ${err.message}`);
      throw err;
    }
  });

  // POST: Create Test Agent
  ipcMain.handle('api:agents:createTest', async (event, { name, role }) => {
    try {
      const params = new URLSearchParams({ name, role });
      const response = await fetch(
        `http://localhost:8000/api/test/create-agent?${params}`,
        { method: 'GET' }
      );
      return await response.json();
    } catch (err) {
      logger.error(`IPC agents:createTest failed: ${err.message}`);
      throw err;
    }
  });

  // Generic GET handler (for flexibility)
  ipcMain.handle('api:get', async (event, endpoint, queryParams = {}) => {
    try {
      const params = new URLSearchParams(queryParams);
      const query = params.toString() ? `?${params}` : '';
      const response = await fetch(`http://localhost:8000${endpoint}${query}`);
      return await response.json();
    } catch (err) {
      logger.error(`IPC generic:get failed for ${endpoint}: ${err.message}`);
      throw err;
    }
  });

  // Generic POST handler
  ipcMain.handle('api:post', async (event, endpoint, data = {}) => {
    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await response.json();
    } catch (err) {
      logger.error(`IPC generic:post failed for ${endpoint}: ${err.message}`);
      throw err;
    }
  });

  logger.info('✅ IPC bridge initialized with API handlers');
};
