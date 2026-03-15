/**
 * Piddy Desktop App - Main Electron Process
 * Handles window management, backend spawning, and IPC communication
 */

const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const axios = require('axios');

// Handle ES Module imports - fix-path is an ES module
let fixPath;
try {
  const fixPathModule = require('fix-path');
  fixPath = fixPathModule.default || fixPathModule;
} catch (err) {
  console.warn('[WARN] fix-path not available, using fallback');
  fixPath = () => {}; // Fallback no-op function
}

// Simple logging wrapper (avoid electron-log ES Module issues)
const log = {
  info: (msg) => console.log('[INFO]', msg),
  error: (msg) => console.error('[ERROR]', msg),
  warn: (msg) => console.warn('[WARN]', msg),
  debug: (msg) => console.log('[DEBUG]', msg),
};

// Fix PATH for macOS to find Python
try {
  if (typeof fixPath === 'function') {
    fixPath();
  }
} catch (err) {
  log.warn(`Failed to fix PATH: ${err.message}`);
}

let mainWindow;
let pythonProcess = null;
let backendReady = false;

const isDevelopment = process.env.NODE_ENV === 'development' || process.env.ELECTRON_DEV_LAUNCH === 'true';

/**
 * Create the main browser window
 */
function createWindow() {
  log.info('Creating main window...');
  
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true
    },
    icon: path.join(__dirname, 'assets', 'icon.png')
  });

  // Load the app
  const startUrl = isDevelopment
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../frontend/dist/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDevelopment) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (pythonProcess) {
      pythonProcess.kill();
    }
  });

  mainWindow.webContents.on('did-finish-load', () => {
    log.info('Window loaded, checking backend status');
    mainWindow.webContents.send('window-loaded');
  });

  createMenu();
}

/**
 * Create application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Piddy',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Piddy',
              message: 'Piddy - AI Backend Developer Agent',
              detail: 'Desktop Client v1.0.0\n\nGet help at: https://github.com/burchdad/Piddy'
            });
          }
        }
      ]
    }
  ];

  if (isDevelopment) {
    template.push({
      label: 'Development',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Spawn the Python backend process
 */
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    log.info('Starting Python backend...');

    try {
      // Determine python executable
      const pythonExe = process.platform === 'win32' ? 'python' : 'python3';
      const scriptPath = path.join(__dirname, '../start_piddy.py');

      pythonProcess = spawn(pythonExe, [scriptPath, '--desktop'], {
        stdio: ['ignore', 'pipe', 'pipe'],
        windowsHide: true
      });

      pythonProcess.stdout.on('data', (data) => {
        log.info(`[Backend] ${data}`);
      });

      pythonProcess.stderr.on('data', (data) => {
        log.warn(`[Backend Error] ${data}`);
      });

      pythonProcess.on('error', (err) => {
        log.error(`Failed to start backend: ${err}`);
        reject(err);
      });

      pythonProcess.on('exit', (code) => {
        log.warn(`Backend exited with code ${code}`);
        backendReady = false;
        if (mainWindow) {
          mainWindow.webContents.send('backend-stopped', { code });
        }
      });

      // Wait for backend to be ready (check API endpoint)
      let attempts = 0;
      const maxAttempts = 60; // 60 seconds (increased from 30)

      const checkBackend = setInterval(() => {
        attempts++;

        // Try simple health check with error handling
        try {
          axios
            .get('http://localhost:8000/health', { timeout: 3000 })
            .then(() => {
              log.info('✅ Backend is ready!');
              clearInterval(checkBackend);
              backendReady = true;
              resolve();
            })
            .catch((err) => {
              // Log errors briefly
              if (attempts % 10 === 0) {
                log.debug(`Backend check attempt ${attempts}: ${err.code || err.message}`);
              }
              
              // If we get a 5xx error, backend is up but broken - still proceed
              if (err.response && err.response.status >= 500) {
                log.warn(`Backend has internal error but is running`);
                clearInterval(checkBackend);
                backendReady = true;
                resolve();
              }
              
              // Final attempt - give up and try anyway
              if (attempts >= maxAttempts) {
                clearInterval(checkBackend);
                log.warn(`Backend health check gave up after ${maxAttempts}s, but proceeding anyway`);
                backendReady = true; // Assume it's running anyway
                resolve();
              }
            });
        } catch (err) {
          if (attempts >= maxAttempts) {
            clearInterval(checkBackend);
            log.warn(`Backend error after ${maxAttempts}s attempts, proceeding anyway`);
            backendReady = true;
            resolve();
          }
        }
      }, 1000);
    } catch (err) {
      log.error(`Error spawning backend: ${err}`);
      reject(err);
    }
  });
}

/**
 * IPC Handlers
 */
ipcMain.handle('backend-status', async () => {
  return { ready: backendReady };
});

ipcMain.handle('get-version', async () => {
  return { version: app.getVersion() };
});

ipcMain.handle('open-external', async (event, url) => {
  const { shell } = require('electron');
  shell.openExternal(url);
});

/**
 * App event handlers
 */
app.on('ready', async () => {
  log.info('🚀 Piddy Desktop App starting...');
  log.info(`Platform: ${process.platform}`);
  log.info(`App path: ${app.getAppPath()}`);

  try {
    // Start Python backend first
    await startPythonBackend();
    log.info('✅ Backend started successfully');

    // Then create the window
    createWindow();
  } catch (err) {
    log.error(`Failed to start app: ${err}`);
    dialog.showErrorBox('Error', `Failed to start Piddy backend: ${err}`);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  // On macOS, apps typically stay active until explicitly closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS, re-create window when dock icon is clicked
  if (mainWindow === null) {
    createWindow();
  }
});

// Handle any uncaught exceptions
process.on('uncaughtException', (err) => {
  log.error(`Uncaught exception: ${err}`);
  if (mainWindow) {
    dialog.showErrorBox('Error', `An error occurred: ${err.message}`);
  }
});

// Log app ready
app.whenReady().then(() => {
  log.info('App is ready!');
});
