/**
 * IPC Bridge for API Communication
 * Now uses direct RPC calls instead of HTTP
 * Zero network hops, direct Python function execution
 * 
 * Usage in frontend:
 *   const data = await window.piddy.api.system.overview();
 *   const result = await window.piddy.api.agents.create({name: 'Bot'});
 */

const { ipcMain } = require('electron');

let pythonBridge = null;

// Setup IPC handlers for all backend APIs
function setupIPCBridge(bridge) {
  pythonBridge = bridge;
  console.log('[IPC Bridge] Initializing API handlers with RPC bridge...');
  
  /**
   * System Endpoints - Direct RPC calls
   */
  ipcMain.handle('api:system:overview', async () => {
    try {
      return await pythonBridge.call('system.overview');
    } catch (err) {
      console.error('[IPC] system:overview failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:health', async () => {
    try {
      return await pythonBridge.call('system.health');
    } catch (err) {
      console.error('[IPC] system:health failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:config', async () => {
    try {
      return await pythonBridge.call('system.config');
    } catch (err) {
      console.error('[IPC] system:config failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:metrics', async () => {
    try {
      return await pythonBridge.call('system.metrics');
    } catch (err) {
      console.error('[IPC] system:metrics failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:logs', async (event, filters) => {
    try {
      return await pythonBridge.call('system.logs', [filters]);
    } catch (err) {
      console.error('[IPC] system:logs failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:system:status', async () => {
    try {
      return await pythonBridge.call('system.status');
    } catch (err) {
      console.error('[IPC] system:status failed:', err.message);
      throw err;
    }
  });

  /**
   * Agent Endpoints - Direct RPC calls
   */
  ipcMain.handle('api:agents:list', async () => {
    try {
      return await pythonBridge.call('agents.list');
    } catch (err) {
      console.error('[IPC] agents:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:get', async (event, agentId) => {
    try {
      return await pythonBridge.call('agents.get', [agentId]);
    } catch (err) {
      console.error('[IPC] agents:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:create', async (event, config) => {
    try {
      return await pythonBridge.call('agents.create', [config]);
    } catch (err) {
      console.error('[IPC] agents:create failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:update', async (event, agentId, config) => {
    try {
      return await pythonBridge.call('agents.update', [agentId, config]);
    } catch (err) {
      console.error('[IPC] agents:update failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:agents:delete', async (event, agentId) => {
    try {
      return await pythonBridge.call('agents.delete', [agentId]);
    } catch (err) {
      console.error('[IPC] agents:delete failed:', err.message);
      throw err;
    }
  });

  /**
   * Message Endpoints - Direct RPC calls
   */
  ipcMain.handle('api:messages:list', async (event, filters) => {
    try {
      return await pythonBridge.call('messages.list', [filters]);
    } catch (err) {
      console.error('[IPC] messages:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:messages:get', async (event, messageId) => {
    try {
      return await pythonBridge.call('messages.get', [messageId]);
    } catch (err) {
      console.error('[IPC] messages:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:messages:send', async (event, message) => {
    try {
      return await pythonBridge.call('messages.send', [message]);
    } catch (err) {
      console.error('[IPC] messages:send failed:', err.message);
      throw err;
    }
  });

  /**
   * Decision Endpoints - Direct RPC calls
   */
  ipcMain.handle('api:decisions:list', async (event, filters) => {
    try {
      return await pythonBridge.call('decisions.list', [filters]);
    } catch (err) {
      console.error('[IPC] decisions:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:decisions:get', async (event, decisionId) => {
    try {
      return await pythonBridge.call('decisions.get', [decisionId]);
    } catch (err) {
      console.error('[IPC] decisions:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:decisions:create', async (event, decision) => {
    try {
      return await pythonBridge.call('decisions.create', [decision]);
    } catch (err) {
      console.error('[IPC] decisions:create failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:decisions:update', async (event, decisionId, decision) => {
    try {
      return await pythonBridge.call('decisions.update', [decisionId, decision]);
    } catch (err) {
      console.error('[IPC] decisions:update failed:', err.message);
      throw err;
    }
  });

  /**
   * Mission Endpoints - Direct RPC calls
   */
  ipcMain.handle('api:missions:list', async (event, filters) => {
    try {
      return await pythonBridge.call('missions.list', [filters]);
    } catch (err) {
      console.error('[IPC] missions:list failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:get', async (event, missionId) => {
    try {
      return await pythonBridge.call('missions.get', [missionId]);
    } catch (err) {
      console.error('[IPC] missions:get failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:create', async (event, mission) => {
    try {
      return await pythonBridge.call('missions.create', [mission]);
    } catch (err) {
      console.error('[IPC] missions:create failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:update', async (event, missionId, mission) => {
    try {
      return await pythonBridge.call('missions.update', [missionId, mission]);
    } catch (err) {
      console.error('[IPC] missions:update failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:missions:execute', async (event, missionId) => {
    try {
      return await pythonBridge.call('missions.execute', [missionId]);
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
      // Create function name from endpoint
      const funcName = endpoint.replace(/^\/api\//, '').replace(/\//g, '.');
      return await pythonBridge.call(funcName, [], queryParams);
    } catch (err) {
      console.error('[IPC] generic GET failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:post', async (event, endpoint, data) => {
    try {
      const funcName = endpoint.replace(/^\/api\//, '').replace(/\//g, '.');
      return await pythonBridge.call(funcName, [data]);
    } catch (err) {
      console.error('[IPC] generic POST failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:put', async (event, endpoint, data) => {
    try {
      const funcName = endpoint.replace(/^\/api\//, '').replace(/\//g, '.');
      return await pythonBridge.call(funcName, [data]);
    } catch (err) {
      console.error('[IPC] generic PUT failed:', err.message);
      throw err;
    }
  });

  ipcMain.handle('api:delete', async (event, endpoint) => {
    try {
      const funcName = endpoint.replace(/^\/api\//, '').replace(/\//g, '.');
      return await pythonBridge.call(funcName, []);
    } catch (err) {
      console.error('[IPC] generic DELETE failed:', err.message);
      throw err;
    }
  });

  console.log('[IPC Bridge] All API handlers registered successfully with RPC');
}

module.exports = setupIPCBridge;
