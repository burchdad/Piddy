# 🎯 Piddy Dashboard

Real-time monitoring and observability dashboard for the Piddy autonomous system. Monitor agents, view logs, track metrics, and observe AI-to-AI communication.

## Features

✨ **Comprehensive Monitoring**
- Real-time system overview and health status
- Agent status tracking with reputation scores
- Live agent-to-agent message board (read-only)
- System logs with filtering and search
- Test results and performance metrics
- Phase deployment tracking
- Security audit results and compliance status

🚀 **Real-Time Updates**
- WebSocket support for live logs and messages
- Polling-based data fetching for reliability
- Configurable refresh intervals
- Auto-reconnection on connection loss

🎨 **Modern UI**
- Dark theme optimized for operations
- Responsive design for desktop and tablets
- Collapsible sidebar navigation
- Component-based architecture
- Smooth animations and transitions

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Overview.jsx       # Dashboard homepage
│   │   ├── Agents.jsx         # Agent monitoring
│   │   ├── Messages.jsx       # Agent message board
│   │   ├── Logs.jsx           # Log viewer
│   │   ├── Tests.jsx          # Test results
│   │   ├── Metrics.jsx        # Performance metrics
│   │   ├── Phases.jsx         # Phase tracking
│   │   ├── Security.jsx       # Security audit results
│   │   └── Sidebar.jsx        # Navigation sidebar
│   ├── styles/
│   │   ├── App.css            # Main app styles
│   │   └── components.css     # Component styles
│   ├── App.jsx                # Main app component
│   └── main.jsx               # React entry point
├── index.html                 # HTML entry point
├── vite.config.js             # Vite configuration
├── package.json               # Dependencies
├── .env.example               # Environment template
├── .eslintrc.json             # ESLint config
├── .prettierrc.json           # Prettier config
└── README.md                  # This file
```

## Prerequisites

- Node.js 16+ 
- npm 8+
- Piddy backend service running (or use mock data for testing)

## Installation

1. **Clone the repository** (if not already done):
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Create environment file** (optional):
```bash
cp .env.example .env
```

Edit `.env` if needed to change API endpoints.

## Development

Start the development server:

```bash
npm run dev
```

The dashboard will open at `http://localhost:3000` and automatically reload on file changes.

### Development Features
- Hot module replacement (HMR)
- Proxy to backend API at `http://127.0.0.1:8000`
- Mock data if backend is unavailable
- Source maps for debugging

## Build

Create a production build:

```bash
npm run build
```

Output will be in the `dist/` directory.

## Deployment

### Web Deployment (Static Files)

1. Build the project: `npm run build`
2. Upload contents of `dist/` to your web server
3. Configure API endpoint in environment variables (see Configuration)
4. Ensure CORS is properly configured on backend

### Docker Deployment

```bash
# Build Docker image
docker build -t piddy-frontend:latest .

# Run container
docker run -p 3000:3000 \
  -e VITE_API_URL=http://backend:8000 \
  piddy-frontend:latest
```

### Electron/Desktop Deployment

For desktop app deployment:

1. Build frontend: `npm run build`
2. See [DESKTOP_BUILD_GUIDE.md](../DESKTOP_BUILD_GUIDE.md) for desktop packaging
3. Pre-load API is configured in Electron preload script
4. Backend URL is injected via `window.piddy.backendUrl`

## Testing

Run tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm test -- --watch
```

## Linting & Formatting

Check code quality:

```bash
npm run lint
```

Auto-format code:

```bash
npm run format
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
VITE_REFRESH_INTERVAL=30000
```

### API Integration

The dashboard connects to the Piddy backend via REST API and WebSocket:

- **REST Endpoints**: `/api/*` routes for data fetching
- **WebSocket**: `/ws/*` routes for real-time streams
- **Mock Mode**: If backend unavailable, uses generated mock data

## Dashboard Pages

### 📊 Overview
Main dashboard showing:
- System health status
- Key metrics (agents, messages, phases, security issues)
- Recent activities
- Quick stats

### 🤖 Agents
Monitor intelligent agents:
- Agent ID and role
- Online/offline status
- Reputation score
- Success rate
- Messages sent/pending

### 💬 Messages
Real-time AI-to-AI communication:
- Message type filtering
- Priority color coding
- Message statistics
- Auto-scrolling feed
- Read-only observation (secure)

### 📝 Logs
System log viewer:
- Real-time log stream
- Level-based filtering (INFO, WARNING, ERROR, DEBUG)
- Source component identification
- Expandable JSON details
- Timestamp tracking

### ✅ Tests
Test results dashboard:
- Test pass/fail/skip status
- Total tests and pass rate
- Execution duration
- Test history

### 📈 Metrics
Performance analytics:
- System performance metrics
- Agent reputation analytics
- Success rate tracking
- Threshold indicators
- Trend visualization

### 🚀 Phases
Deployment phase tracking:
- Phase status (pending, in_progress, completed, failed)
- Progress percentage
- Timeline information
- Phase details

### 🔒 Security
Security and compliance:
- Audit results
- Production readiness status
- Critical failures list
- Security checklist
- Pass rate metrics

## API Reference

The dashboard communicates with the Piddy backend API:

### Health & Overview
- `GET /api/health` - Health check
- `GET /api/system/overview` - System overview
- `GET /api/analytics/*` - Analytics data

### Agents
- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Agent details
- `GET /api/agents/{id}/reputation` - Agent reputation

### Messages
- `GET /api/messages` - Get messages
- `WS /ws/messages` - Real-time message stream

### Logs
- `GET /api/logs` - Get system logs
- `GET /api/logs/{source}` - Logs from source
- `WS /ws/logs` - Real-time log stream

### Other
- `GET /api/tests` - Test results
- `GET /api/metrics/performance` - Performance metrics
- `GET /api/phases` - Phase status
- `GET /api/security/audit` - Security audit results

See `src/dashboard_api.py` for full endpoint documentation.

## Troubleshooting

### API Connection Error

If you see "Failed to connect to API":

1. Ensure Piddy backend is running on `http://127.0.0.1:8000`
2. Check Firefox/Chrome console for CORS errors
3. Mock data will be used automatically if backend unavailable

### Missing Data

1. Check browser console for fetch errors
2. Verify backend API is returning data
3. Clear browser cache and refresh
4. Check polling intervals in `.env`

### Build Errors

1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear build cache: `rm -rf dist`
3. Check Node.js version: `node --version` (16+)

## Desktop Installation

To package the dashboard as a desktop application:

### Option 1: Electron

```bash
# Install Electron
npm install --save-dev electron

# Create electron main process
# See Electron documentation for setup
```

### Option 2: Tauri

```bash
# Install Tauri
npm install --save-dev tauri

# Initialize Tauri project
npm run tauri init

# Build desktop app
npm run tauri build
```

## Performance

### Optimization Tips

1. **Reduce Polling Intervals**: Adjust `VITE_*_POLL_INTERVAL` in `.env`
2. **Enable WebSockets**: Set `VITE_ENABLE_WEBSOCKETS=true` for real-time
3. **Disable Unused Pages**: Comment out unused components in App.jsx
4. **Use Production Build**: Always use `npm run build` for deployment

### Resource Usage

- Memory: ~50-100MB for typical operation
- CPU: <2% idle, <10% with active updates
- Network: ~1KB/s with real-time updates

## Contributing

To contribute to the dashboard:

1. Create a feature branch
2. Make changes following code style (ESLint + Prettier)
3. Test thoroughly
4. Submit pull request

## License

See LICENSE file in root directory.

## Support

For issues or questions:

1. Check existing documentation
2. Review browser console for errors
3. Check backend API status
4. Enable debug logging in `.env`

## Roadmap

Future features:
- [ ] Dark/Light theme toggle
- [ ] Custom dashboard layouts
- [ ] Alert notifications
- [ ] Historical data graphs
- [ ] Message search/filtering
- [ ] Export data capabilities
- [ ] Multi-user support
- [ ] Mobile app version
