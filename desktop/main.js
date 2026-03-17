/**
 * Piddy Desktop App - Main Electron Process
 * Handles window management, backend spawning, and IPC communication
 */

const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const axios = require('axios');
const http = require('http');

// IPC Bridge and port finding for zero-port architecture
const setupIPCBridge = require('./ipc-bridge');
const { getPort } = require('./port-finder');
const PythonBridge = require('./python-bridge');
const { StreamManager } = require('./stream-manager');

// Handle ES Module imports - fix-path is an ES module
let fixPath;
try {
  const fixPathModule = require('fix-path');
  fixPath = fixPathModule.default || fixPathModule;
} catch (err) {
  console.warn('[WARN] fix-path not available, using fallback');
  fixPath = () => {}; // Fallback no-op function
}

// Setup logging to both console and file
// Create a logs directory relative to the app's install location for easy debugging
const homeDir = process.env.USERPROFILE || process.env.HOME || process.env.HOMEPATH;
const logsDir = path.join(homeDir, '.piddy_logs');
try {
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }
} catch (err) {
  console.log('Could not create logs directory:', err.message);
}
const logFilePath = path.join(logsDir, 'piddy_main.log');
const logStream = fs.createWriteStream(logFilePath, { flags: 'a' });

// Log startup info immediately
console.log(`\n${'='.repeat(80)}`);
console.log(`[STARTUP] Piddy App Starting - ${new Date().toISOString()}`);
console.log(`[STARTUP] Logs: ${logFilePath}`);
console.log(`[STARTUP] Platform: ${process.platform}`);
console.log(`[STARTUP] App Path: ${__dirname}`);
console.log(`${'='.repeat(80)}\n`);

// Simple logging wrapper (avoid electron-log ES Module issues)
const log = {
  info: (msg) => {
    console.log('[INFO]', msg);
    logStream.write(`[INFO] ${msg}\n`);
  },
  error: (msg) => {
    console.error('[ERROR]', msg);
    logStream.write(`[ERROR] ${msg}\n`);
  },
  warn: (msg) => {
    console.warn('[WARN]', msg);
    logStream.write(`[WARN] ${msg}\n`);
  },
  debug: (msg) => {
    console.log('[DEBUG]', msg);
    logStream.write(`[DEBUG] ${msg}\n`);
  },
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
let splashWindow;
let pythonProcess = null;
let backendReady = false;
let staticServerReady = false;

const isDevelopment = process.env.NODE_ENV === 'development' || process.env.ELECTRON_DEV_LAUNCH === 'true';

/**
 * Resolve file paths correctly for both dev and packaged modes
 * In dev: files are relative to ../
 * In packaged: files are in the resources/ directory (not inside asar)
 */
function getResourcePath(relativePath) {
  if (isDevelopment) {
    // In development, files are outside the app directory
    return path.join(__dirname, '..', relativePath);
  } else {
    // In packaged app with extraResources, files are in resources/ directory
    // app.getAppPath() returns /resources/app.asar, so go up one level
    return path.join(app.getAppPath(), '..', relativePath);
  }
}

/**
 * Create a splash screen window showing loading progress
 */
function createSplashScreen() {
  log.info('Creating splash screen...');
  
  splashWindow = new BrowserWindow({
    width: 500,
    height: 650,
    minWidth: 400,
    minHeight: 500,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true
    },
    frame: false,  // Frameless window for clean look
    alwaysOnTop: true,  // Keep on top during loading
    skipTaskbar: true,  // Don't show in taskbar
    show: true,  // Show immediately
    transparent: false,
    icon: path.join(__dirname, 'assets', 'icon.png')
  });

  const splashPath = isDevelopment 
    ? path.join(__dirname, 'splash.html')
    : path.join(app.getAppPath(), '..', 'splash.html');

  log.info(`Loading splash from: ${splashPath}`);
  
  try {
    splashWindow.loadURL(`file://${splashPath}`);
  } catch (err) {
    log.error(`Failed to load splash screen: ${err}`);
  }

  // Optional: Open dev tools for splash during development
  // if (isDevelopment) {
  //   splashWindow.webContents.openDevTools();
  // }

  return splashWindow;
}

/**
 * Send status update to splash screen
 */
function updateSplashStatus(message, progress = 10) {
  if (splashWindow && !splashWindow.isDestroyed()) {
    try {
      splashWindow.webContents.send('splash-status', { message, progress });
      log.debug(`Splash: ${message}`);
    } catch (err) {
      log.debug(`Could not update splash: ${err.message}`);
    }
  }
}

/**
 * Complete splash screen and close it
 */
function completeSplash() {
  if (splashWindow && !splashWindow.isDestroyed()) {
    try {
      splashWindow.webContents.send('splash-complete');
      setTimeout(() => {
        if (splashWindow && !splashWindow.isDestroyed()) {
          splashWindow.close();
          splashWindow = null;
        }
      }, 500);
    } catch (err) {
      log.debug(`Error completing splash: ${err.message}`);
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.close();
      }
      splashWindow = null;
    }
  }
}

/**
 * Start a simple static file server for the frontend
 * Avoids file:// CORS issues in Electron
 */
function startStaticServer() {
  return new Promise((resolve, reject) => {
    const distPath = getResourcePath('frontend/dist');
    log.info(`Attempting to serve static files from: ${distPath}`);
    
    if (!fs.existsSync(distPath)) {
      log.warn(`Frontend dist directory not found at ${distPath}, UI may not load`);
      resolve(null);
      return;
    }
    
    log.info(`✅ Found frontend dist directory`);

    
    const server = http.createServer((req, res) => {
      // Remove query string and decode URL
      let filePath = path.join(distPath, req.url === '/' ? 'index.html' : req.url);
      
      // Prevent directory traversal
      if (!filePath.startsWith(distPath)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
      }
      
      // Try to serve the file
      fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
          // If not found, serve index.html (SPA routing)
          filePath = path.join(distPath, 'index.html');
        }
        
        fs.readFile(filePath, (err, data) => {
          if (err) {
            res.writeHead(404);
            res.end('Not Found');
            return;
          }
          
          // Set appropriate content type
          const ext = path.extname(filePath);
          const contentTypes = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
          };
          
          const contentType = contentTypes[ext] || 'application/octet-stream';
          res.writeHead(200, { 'Content-Type': contentType });
          res.end(data);
        });
      });
    });
    
    // Find an available port
    let port = 4000;
    const tryPort = () => {
      server.listen(port, 'localhost', () => {
        log.info(`Static server running on http://localhost:${port}`);
        staticServerReady = true;
        resolve(`http://localhost:${port}`);
      }).on('error', (err) => {
        if (err.code === 'EADDRINUSE') {
          port++;
          if (port < 4100) {
            tryPort();
          } else {
            reject(new Error('Could not find available port for static server'));
          }
        } else {
          reject(err);
        }
      });
    };
    
    tryPort();
  });
}

/**
 * Create the main browser window
 */
function createWindow() {
  log.info('Creating main window...');
  console.log('[WINDOW] Starting BrowserWindow creation');
  
  try {
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

    log.info('BrowserWindow created successfully');
    console.log('[WINDOW] BrowserWindow created, PID:', mainWindow.webContents.getProcessId?.());

    // Use static server for production to avoid file:// CORS issues
    if (isDevelopment) {
      log.info('Development mode - loading from localhost:3000');
      mainWindow.loadURL('http://localhost:3000');
      mainWindow.webContents.openDevTools();
    } else {
      log.info('Production mode - starting static server');
      console.log('[WINDOW] About to setup UI with static server');
      
      // For production, use the static server we started earlier
      const setupUI = async () => {
        try {
          console.log('[WINDOW] setupUI starting');
          const serverUrl = await startStaticServer();
          console.log('[WINDOW] setupUI got serverUrl:', serverUrl);
          
          if (serverUrl) {
            log.info(`Loading UI from: ${serverUrl}`);
            console.log('[WINDOW] Loading URL:', serverUrl);
            mainWindow.loadURL(serverUrl);
          } else {
            log.error('Failed to start static server, falling back to file://');
            const fallbackPath = `file://${path.join(__dirname, '../frontend/dist/index.html')}`;
            log.info(`Loading from: ${fallbackPath}`);
            mainWindow.loadURL(fallbackPath);
          }
        } catch (err) {
          log.error(`setupUI error: ${err}`);
          console.error('[WINDOW] setupUI error:', err);
          const fallbackPath = `file://${path.join(__dirname, '../frontend/dist/index.html')}`;
          mainWindow.loadURL(fallbackPath);
        }
      };
      
      console.log('[WINDOW] Calling setupUI');
      setupUI().catch(err => {
        log.error(`setupUI promise error: ${err}`);
        console.error('[WINDOW] setupUI promise error:', err);
      });
    }

    log.info('Window loading initiated');
    console.log('[WINDOW] Window loading initiated');

    // Always open dev tools for debugging
    setTimeout(() => {
      if (!isDevelopment && mainWindow) {
        mainWindow.webContents.openDevTools();
      }
    }, 1000);

    mainWindow.on('closed', () => {
      log.info('Window closed by user');
      mainWindow = null;
      if (pythonProcess) {
        pythonProcess.kill();
      }
    });

    mainWindow.webContents.on('did-finish-load', () => {
      log.info('Window loaded, checking backend status');
      console.log('[WINDOW] did-finish-load event fired');
      updateSplashStatus('Dashboard ready!', 95);
      
      // Close splash screen and show main window
      setTimeout(() => {
        completeSplash();
        log.info('Splash screen closed, main window visible');
      }, 500);
      
      mainWindow.webContents.send('window-loaded');
    });

    mainWindow.webContents.on('crashed', () => {
      log.error('Renderer process crashed!');
      console.error('[WINDOW] Renderer crashed');
    });

    mainWindow.on('unresponsive', () => {
      log.warn('Window became unresponsive');
      console.warn('[WINDOW] Window unresponsive');
    });

    mainWindow.webContents.on('console-message', (level, message, line, sourceId) => {
      console.log(`[RENDERER ${level}] ${message} (${sourceId}:${line})`);
    });

    createMenu();
  } catch (err) {
    log.error(`Error creating window: ${err}`);
    console.error('[WINDOW] Error creating window:', err);
    throw err;
  }
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
 * Find Python executable path or bundled backend
 * Priority: bundled backend > Python executable > system Python
 */
function findPython() {
  log.info('🔍 Searching for backend executable...');
  
  // FIRST: Try to find bundled backend executable
  const bundledNames = process.platform === 'win32' 
    ? ['piddy-backend.exe', 'piddy-backend']
    : ['piddy-backend', 'piddy-backend.exe'];
  
  // Check in resources directory (packaged app)
  const resourcesPath = getResourcePath('');
  for (const name of bundledNames) {
    const bundledPath = path.join(resourcesPath, name);
    try {
      if (fs.existsSync(bundledPath)) {
        log.info(`✅ Found bundled backend: ${bundledPath}`);
        return bundledPath;
      }
    } catch (err) {
      log.debug(`  Error checking bundled path: ${err.message}`);
    }
  }
  
  // Check in app root (development mode)
  for (const name of bundledNames) {
    const devPath = path.join(__dirname, '..', name);
    try {
      if (fs.existsSync(devPath)) {
        log.info(`✅ Found bundled backend (dev): ${devPath}`);
        return devPath;
      }
    } catch (err) {
      log.debug(`  Error checking dev path: ${err.message}`);
    }
  }
  
  log.info('ℹ️  Bundled backend not found, searching for Python...');
  
  // FALLBACK: Search for Python executable
  log.info('🔍 Searching for Python executable...');
  
  // On Windows, try multiple common paths
  if (process.platform === 'win32') {
    const windowsPaths = [
      'python.exe',
      'python3.exe',
      // Root-level Python installations (most common for standalone installs)
      'C:\\Python313\\python.exe',
      'C:\\Python312\\python.exe',
      'C:\\Python311\\python.exe',
      'C:\\Python310\\python.exe',
      'C:\\Python39\\python.exe',
      // Program Files installations
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python313', 'python.exe'),
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python312', 'python.exe'),
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python311', 'python.exe'),
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python310', 'python.exe'),
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python39', 'python.exe'),
      path.join(process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'Python313', 'python.exe'),
      path.join(process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'Python312', 'python.exe'),
      path.join(process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'Python311', 'python.exe'),
      path.join(process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'Python310', 'python.exe'),
      path.join(process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)', 'Python39', 'python.exe'),
      path.join(process.env.APPDATA || '', 'Python', 'Python313', 'python.exe'),
      path.join(process.env.APPDATA || '', 'Python', 'Python312', 'python.exe'),
      path.join(process.env.APPDATA || '', 'Python', 'Python311', 'python.exe'),
    ];
    
    log.debug(`Searching Windows paths: ${windowsPaths.join(', ')}`);
    
    for (const pythonPath of windowsPaths) {
      try {
        log.debug(`  Checking: ${pythonPath}`);
        if (fs.existsSync(pythonPath)) {
          log.info(`✅ Found Python at: ${pythonPath}`);
          return pythonPath;
        }
      } catch (err) {
        log.debug(`    Error checking path: ${err.message}`);
      }
    }
  } else {
    // On macOS/Linux, try common paths
    const unixPaths = ['python3', 'python', '/usr/bin/python3', '/usr/bin/python'];
    for (const pythonPath of unixPaths) {
      try {
        log.debug(`  Checking: ${pythonPath}`);
        const result = require('child_process').spawnSync(pythonPath, ['--version'], { 
          stdio: 'pipe',
          timeout: 2000 
        });
        if (result.status === 0) {
          log.info(`✅ Found Python at: ${pythonPath}`);
          return pythonPath;
        }
      } catch (err) {
        log.debug(`    Error checking path: ${err.message}`);
      }
    }
  }
  
  log.error('❌ Python executable not found!');
  log.error(`   PATH: ${process.env.PATH}`);
  return null;
}

/**
 * Spawn the Python backend process
 */
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    console.log('[PROMISE] startPythonBackend promise created');
    log.info('Starting Python backend...');
    console.log('[PROMISE] Logged "Starting Python backend"');
    updateSplashStatus('Locating Python...', 5);

    try {
      // Find python executable
      console.log('[PROMISE] About to call findPython()');
      log.info('Step 1: Searching for Python...');
      updateSplashStatus('Finding Python executable...', 8);
      const pythonExe = findPython();
      console.log('[PROMISE] findPython() returned:', pythonExe);
      log.info(`Step 2: findPython() returned: ${pythonExe}`);
      
      if (!pythonExe) {
        const errorMsg = 'Python not found on system. Please ensure Python 3.9+ is installed and in PATH.';
        log.error(errorMsg);
        updateSplashStatus('❌ Python not found', 100);
        reject(new Error(errorMsg));
        return;
      }

      updateSplashStatus('Validating backend files...', 12);
      const scriptPath = getResourcePath('start_piddy.py');
      log.info(`Python script path: ${scriptPath}`);
      
      if (!fs.existsSync(scriptPath)) {
        const errorMsg = `start_piddy.py not found at ${scriptPath}. Backend files may be missing from distribution.`;
        log.error(errorMsg);
        updateSplashStatus('❌ Backend files missing', 100);
        reject(new Error(errorMsg));
        return;
      }
      
      log.info(`✅ Found start_piddy.py`);
      updateSplashStatus('Spawning backend process...', 20);

      // Set working directory to the directory containing start_piddy.py
      const scriptDir = path.dirname(scriptPath);
      log.info(`Backend working directory: ${scriptDir}`);
      
      // Determine if we're using bundled binary or Python
      const isBundledBinary = pythonExe.includes('piddy-backend');
      let spawnArgs = [];
      let spawnCmd = pythonExe;
      
      if (isBundledBinary) {
        log.info(`Using bundled backend binary: ${pythonExe}`);
        spawnArgs = []; // Binary runs standalone, no args needed
      } else {
        log.info(`Using Python interpreter: ${pythonExe}`);
        spawnArgs = [scriptPath, '--desktop', '--rpc-mode'];  // Add --rpc-mode for direct RPC communication
      }
      
      log.info(`Step 3: About to spawn: ${spawnCmd} ${spawnArgs.join(' ')}`);
      log.info(`Step 3b: Working dir: ${scriptDir}`);
      log.info(`Step 3c: Stdio config: ['ignore', 'pipe', 'pipe']`);
      
      pythonProcess = spawn(spawnCmd, spawnArgs, {
        stdio: ['pipe', 'pipe', 'pipe'],  // Changed to 'pipe' for stdin to support RPC communication
        windowsHide: true,
        cwd: scriptDir,
        env: { ...process.env }
      });

      log.info(`Step 4: Process spawned, PID: ${pythonProcess ? pythonProcess.pid : 'null'}`);

      // Initialize Python RPC bridge
      console.log('[BRIDGE] Initializing Python RPC bridge...');
      let pythonBridge;
      try {
        pythonBridge = new PythonBridge(pythonProcess);
        console.log('[BRIDGE] Python RPC bridge created');
      } catch (err) {
        log.error(`Failed to initialize Python bridge: ${err}`);
        pythonProcess.kill();
        reject(err);
        return;
      }

      // ✅ CRITICAL FIX: Resolve immediately after spawn succeeds - don't wait for process exit!
      // The backend runs indefinitely, so we resolve here to allow the UI to start
      backendReady = true;
      updateSplashStatus('Backend services running...', 30);
      
      // Store bridge for later use
      global.pythonBridge = pythonBridge;
      
      // Initialize stream manager for real-time updates
      global.streamManager = new StreamManager(pythonBridge);
      log.info("✅ Stream manager initialized for real-time updates");
      
      resolve({ process: pythonProcess, bridge: pythonBridge });

      let backendOutput = '';
      let backendErrors = '';

      pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        backendOutput += output;
        log.info(`[Backend] ${output}`);
      });

      pythonProcess.stderr.on('data', (data) => {
        const error = data.toString();
        backendErrors += error;
        log.warn(`[Backend Error] ${error}`);
      });

      pythonProcess.on('error', (err) => {
        log.error(`❌ Failed to spawn backend process: ${err.message}`);
        log.error(`   Error code: ${err.code}`);
        if (err.code === 'ENOENT') {
          log.error(`   Python executable not found at: ${pythonExe}`);
        }
        if (!backendReady) {
          reject(err);
        }
      });

      pythonProcess.on('exit', (code, signal) => {
        log.warn(`Backend process exited with code ${code}, signal ${signal}`);
        log.warn(`Last output: ${backendOutput.slice(-200)}`);
        if (backendErrors) {
          log.error(`Last error: ${backendErrors.slice(-200)}`);
        }
        backendReady = false;
        if (mainWindow) {
          mainWindow.webContents.send('backend-stopped', { code, signal });
        }
      });
    } catch (err) {
      log.error(`Error spawning backend: ${err}`);
      reject(err);
    }
  });
}

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

ipcMain.handle('get-logs', async () => {
  // Return the main process log file path for debugging
  return { logPath: logFilePath };
});

/**
 * App event handlers
 */
app.on('ready', async () => {
  log.info('🚀 Piddy Desktop App starting...');
  log.info(`Platform: ${process.platform}`);
  log.info(`App path: ${app.getAppPath()}`);

  try {
    // Create splash screen immediately
    createSplashScreen();
    updateSplashStatus('Starting Python backend...', 15);

    // Start Python backend first
    await startPythonBackend();
    updateSplashStatus('Backend started successfully', 35);
    log.info('✅ Backend started successfully');

    updateSplashStatus('Initializing static server...', 50);
    
    // Then create the main window
    createWindow();
    
    // Setup IPC bridge for zero-port API communication
    log.info('Setting up IPC bridge for zero-port architecture...');
    setupIPCBridge(global.pythonBridge);
    log.info('✅ IPC bridge initialized with RPC');
    
    updateSplashStatus('Loading frontend...', 75);
    
  } catch (err) {
    log.error(`Failed to start app: ${err}`);
    updateSplashStatus(`Error: ${err}`, 100);
    
    setTimeout(() => {
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.close();
      }
      dialog.showErrorBox('Error', `Failed to start Piddy backend: ${err}`);
      app.quit();
    }, 1500);
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
  console.error('[UNCAUGHT]', err);
  if (mainWindow) {
    dialog.showErrorBox('Error', `An error occurred: ${err.message}`);
  }
});

// Log app ready
app.whenReady().then(() => {
  log.info('App is ready!');
});
