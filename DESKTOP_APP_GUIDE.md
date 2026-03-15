# 🚀 Piddy Desktop Application

**Download Piddy once, click to run. That's it!**

Piddy is now available as a standalone desktop application for Windows, macOS, and Linux. No server setup needed - everything runs locally on your machine.

## 📥 Installation

### Windows
1. Download `Piddy-Setup.exe` from [Releases](https://github.com/burchdad/Piddy/releases)
2. Run the installer
3. Click "Piddy" from your Start Menu or desktop

### macOS
1. Download `Piddy-1.0.0.dmg` from [Releases](https://github.com/burchdad/Piddy/releases)
2. Open the DMG file
3. Drag "Piddy" to Applications folder
4. Launch from Applications

### Linux
1. Download `Piddy-1.0.0.AppImage` from [Releases](https://github.com/burchdad/Piddy/releases)
2. Make it executable:
   ```bash
   chmod +x Piddy-1.0.0.AppImage
   ```
3. Double-click to run, or from terminal:
   ```bash
   ./Piddy-1.0.0.AppImage
   ```

## 🎯 Features

✅ **One-Click Launch** - No configuration needed  
✅ **Local Storage** - All data stays on your machine  
✅ **Auto-Update** - Get new features automatically  
✅ **Chat Interface** - Talk to Piddy just like Slack  
✅ **Full Power** - Access to all Piddy capabilities  

## 🏃 First Run

When you launch Piddy for the first time:

1. **Backend Starting** - Piddy initializes the AI engine (takes ~10 seconds)
2. **Dashboard Opens** - Your browser window appears
3. **Ready to Chat** - Start asking Piddy to build and fix code!

> 💡 If you don't see the dashboard after 20 seconds, check the terminal output for errors.

## 💬 Using Piddy

### Basic Chat
- Type your request in the chat input
- Press Enter or click Send
- Piddy analyzes your request and responds with:
  - Code changes
  - File modifications  
  - Build status
  - Testing results

### Example Requests
```
"Create a REST API endpoint for user authentication"
"Fix the bug in auth_service.py"
"Write tests for the payment module"
"Refactor the database queries for performance"
"Deploy version 2.1.0 to production"
```

### Features & Commands
- **Code Analysis** - Piddy reviews your code
- **Testing** - Automatic test generation and validation
- **Git Integration** - Commit, push, PR generation
- **Deployment** - GitHub Actions, Docker, Kubernetes
- **Monitoring** - System health and performance tracking

## ⚙️ Configuration

### User Settings
Piddy stores settings in `~/.piddy/`:
- `~/.piddy/config.json` - Application settings
- `~/.piddy/data/` - Project data and cache
- `~/.piddy/logs/` - Application logs

### Environment Variables
Create `.piddy/.env` for optional settings:
```bash
OPENAI_API_KEY=sk-...          # For AI model (optional fallback)
GITHUB_TOKEN=ghp_...           # For GitHub integration
SLACK_BOT_TOKEN=xoxb-...       # For Slack notifications
```

## 🔄 Updates

Piddy checks for updates automatically. When an update is available:
1. You'll see a notification
2. Click "Update" to install
3. App restarts with new version

Or manually check: **Help → Check for Updates**

## 📋 Troubleshooting

### App won't start
```bash
# Check logs
cd ~/.piddy/logs
tail -f piddy_desktop_*.log
```

### Backend errors
- Ensure Python 3.9+ is installed
- Check internet connection (for initial model download)

### Out of memory
- Close other applications
- Restart Piddy
- Check the logs for memory issues

### Port conflicts
If port 8000 is already in use:
```bash
# Find what's using it
lsof -i :8000        # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
```

## 🔐 Privacy & Security

✅ **Local First** - Everything runs on your machine  
✅ **No Telemetry** - We don't track your code  
✅ **Open Source** - Inspect the code yourself  
✅ **Encrypted** - All sensitive data is encrypted at rest  

## 📚 Documentation

- [Full Documentation](https://github.com/burchdad/Piddy)
- [API Reference](../API.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)

## 🤝 Support

- **Issues** - Report bugs on [GitHub Issues](https://github.com/burchdad/Piddy/issues)
- **Discussions** - Ask questions in [GitHub Discussions](https://github.com/burchdad/Piddy/discussions)
- **Email** - support@piddy.dev (placeholder)

## 📝 License

MIT License - See [LICENSE](../LICENSE) for details

---

**Made with ❤️ by the Piddy Team**

*Your AI Backend Developer Agent. Desktop Edition.*
