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

const isDevelopment = process.env.NODE_ENV === 'development'
  || process.env.ELECTRON_DEV_LAUNCH === 'true'
  || !app.isPackaged;  // Running from source tree = dev mode

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

    // Always use static server to avoid file:// CORS issues
    // In dev mode, try Vite dev server first, then fall back to static server
    const setupUI = async () => {
      try {
        // In dev mode, check if Vite dev server is running
        if (isDevelopment) {
          try {
            const probe = await new Promise((resolve, reject) => {
              const req = http.get('http://localhost:3000', (res) => resolve(res.statusCode));
              req.on('error', reject);
              req.setTimeout(1000, () => { req.destroy(); reject(new Error('timeout')); });
            });
            if (probe === 200) {
              log.info('Development mode - Vite dev server detected on :3000');
              mainWindow.loadURL('http://localhost:3000');
              mainWindow.webContents.openDevTools();
              return;
            }
          } catch (_) {
            log.info('Vite dev server not running, falling back to static server');
          }
        }

        // Use static server for production build (works in both dev and packaged mode)
        log.info('Starting static file server for frontend/dist...');
        const serverUrl = await startStaticServer();
        
        if (serverUrl) {
          log.info(`Loading UI from: ${serverUrl}`);
          mainWindow.loadURL(serverUrl);
        } else {
          log.error('Failed to start static server, falling back to file://');
          const fallbackPath = `file://${path.join(__dirname, '../frontend/dist/index.html')}`;
          log.info(`Loading from: ${fallbackPath}`);
          mainWindow.loadURL(fallbackPath);
        }
      } catch (err) {
        log.error(`setupUI error: ${err}`);
        const fallbackPath = `file://${path.join(__dirname, '../frontend/dist/index.html')}`;
        mainWindow.loadURL(fallbackPath);
      }
    };
    
    setupUI().catch(err => {
      log.error(`setupUI promise error: ${err}`);
    });

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
 * Create application menu — VS Code-inspired, Piddy-tailored
 */
function createMenu() {
  const nav = (page) => () => {
    if (mainWindow) mainWindow.webContents.send('menu:navigate', page);
  };
  const action = (name) => () => {
    if (mainWindow) mainWindow.webContents.send('menu:action', name);
  };

  const template = [
    {
      label: 'File',
      submenu: [
        { label: 'New Chat', accelerator: 'CmdOrCtrl+N', click: action('new-chat') },
        { type: 'separator' },
        { label: 'Export Data', click: nav('export') },
        { label: 'Settings', accelerator: 'CmdOrCtrl+,', click: nav('settings') },
        { type: 'separator' },
        { label: 'Exit', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() }
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
        { role: 'paste' },
        { role: 'selectAll' },
        { type: 'separator' },
        { label: 'Find in Logs', accelerator: 'CmdOrCtrl+F', click: nav('logs') }
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Toggle Sidebar', accelerator: 'CmdOrCtrl+B', click: action('toggle-sidebar') },
        { label: 'Toggle Chat Panel', accelerator: 'CmdOrCtrl+J', click: action('toggle-chat') },
        { type: 'separator' },
        { label: 'Overview', click: nav('overview') },
        { label: 'System Health', click: nav('doctor') },
        { label: 'Agents', click: nav('agents') },
        { label: 'Missions', click: nav('missions') },
        { type: 'separator' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { role: 'resetZoom' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Go',
      submenu: [
        { label: 'Chat', accelerator: 'CmdOrCtrl+1', click: action('open-chat') },
        { label: 'Overview', accelerator: 'CmdOrCtrl+2', click: nav('overview') },
        { label: 'Health', accelerator: 'CmdOrCtrl+3', click: nav('doctor') },
        { label: 'Skills', accelerator: 'CmdOrCtrl+4', click: nav('skills') },
        { label: 'Agents', accelerator: 'CmdOrCtrl+5', click: nav('agents') },
        { type: 'separator' },
        { label: 'History', click: nav('sessions') },
        { label: 'Logs', click: nav('logs') },
        { label: 'Scanner', click: nav('scanner') },
        { label: 'Updates', click: nav('updater') }
      ]
    },
    {
      label: 'Help',
      submenu: [
        { label: 'Keyboard Shortcuts', accelerator: 'CmdOrCtrl+K CmdOrCtrl+S', click: action('show-shortcuts') },
        { type: 'separator' },
        { label: 'System Health Check', click: nav('doctor') },
        { label: 'Check for Updates', click: nav('updater') },
        { type: 'separator' },
        {
          label: 'About Piddy',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Piddy',
              message: 'Piddy - AI Backend Developer Agent',
              detail: 'Desktop Client v1.0.0\n\nBuilt with Electron + React + Python'
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
 * Detect platform tag for runtime directory naming
 * Returns e.g. 'win32-x64', 'darwin-arm64', 'linux-x64'
 */
function getPlatformTag() {
  const platform = process.platform === 'win32' ? 'win32'
    : process.platform === 'darwin' ? 'darwin' : 'linux';
  const arch = process.arch === 'arm64' ? 'arm64' : 'x64';
  return `${platform}-${arch}`;
}

/**
 * Find Python executable path or bundled backend
 * Priority: bundled backend > embedded runtime (platform-specific) > embedded runtime (generic) > system Python
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
  
  log.info('ℹ️  Bundled backend not found, searching for embedded Python...');
  
  // SECOND: Check platform-specific embedded runtime (cross-platform portable)
  const platformTag = getPlatformTag();
  const projectRoot = path.join(__dirname, '..');
  
  const embeddedPaths = [];
  
  if (process.platform === 'win32') {
    // Windows: platform-specific then generic
    embeddedPaths.push(
      path.join(projectRoot, 'runtime', platformTag, 'python', 'python.exe'),
      path.join(projectRoot, 'runtime', 'python', 'python.exe')
    );
  } else {
    // macOS / Linux: platform-specific then generic
    embeddedPaths.push(
      path.join(projectRoot, 'runtime', platformTag, 'python', 'bin', 'python3'),
      path.join(projectRoot, 'runtime', 'python', 'bin', 'python3')
    );
  }
  
  for (const embeddedPath of embeddedPaths) {
    try {
      if (fs.existsSync(embeddedPath)) {
        log.info(`✅ Found embedded Python: ${embeddedPath}`);
        return embeddedPath;
      }
    } catch (err) {
      log.debug(`  Error checking embedded path: ${err.message}`);
    }
  }
  
  log.info('ℹ️  No embedded Python found, searching system Python...');
  
  // FALLBACK: Search for system Python
  if (process.platform === 'win32') {
    const windowsPaths = [
      'python.exe',
      'python3.exe',
      'C:\\Python313\\python.exe',
      'C:\\Python312\\python.exe',
      'C:\\Python311\\python.exe',
      'C:\\Python310\\python.exe',
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python313', 'python.exe'),
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python312', 'python.exe'),
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python311', 'python.exe'),
      path.join(process.env.PROGRAMFILES || 'C:\\Program Files', 'Python310', 'python.exe'),
    ];
    
    for (const pythonPath of windowsPaths) {
      try {
        if (fs.existsSync(pythonPath)) {
          log.info(`✅ Found system Python: ${pythonPath}`);
          return pythonPath;
        }
      } catch (err) {
        log.debug(`    Error: ${err.message}`);
      }
    }
  } else {
    // macOS/Linux system Python
    const unixPaths = ['python3', 'python', '/usr/bin/python3', '/usr/local/bin/python3', '/usr/bin/python'];
    for (const pythonPath of unixPaths) {
      try {
        const result = require('child_process').spawnSync(pythonPath, ['--version'], { 
          stdio: 'pipe',
          timeout: 2000 
        });
        if (result.status === 0) {
          log.info(`✅ Found system Python: ${pythonPath}`);
          return pythonPath;
        }
      } catch (err) {
        log.debug(`    Error: ${err.message}`);
      }
    }
  }
  
  log.error('❌ Python executable not found!');
  log.error(`   Checked: embedded runtime/${platformTag}/python, runtime/python, system PATH`);
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
        spawnArgs = ['-u', scriptPath, '--desktop', '--rpc-mode'];  // -u for unbuffered stdio, --rpc-mode for direct RPC
      }
      
      log.info(`Step 3: About to spawn: ${spawnCmd} ${spawnArgs.join(' ')}`);
      log.info(`Step 3b: Working dir: ${scriptDir}`);
      log.info(`Step 3c: Stdio config: ['ignore', 'pipe', 'pipe']`);
      
      pythonProcess = spawn(spawnCmd, spawnArgs, {
        stdio: ['pipe', 'pipe', 'pipe'],  // Changed to 'pipe' for stdin to support RPC communication
        windowsHide: true,
        cwd: scriptDir,
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
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
