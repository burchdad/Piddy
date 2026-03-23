# Piddy Slack Integration - Complete Index

Welcome to Piddy's Slack integration documentation! This index helps you find what you need quickly.

## 📚 Documentation Guide

Choose based on your needs:

### 🚀 Just Getting Started?
**Start here:** [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md)
- Quick setup (5 minutes)
- Common commands
- Basic examples
- Emoji reference

### ⚙️ Need to Set Up Slack?
**Read:** [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)
- Step-by-step Slack app creation
- Token configuration
- OAuth setup
- Socket Mode configuration
- Event subscriptions
- Slash commands (optional)
- Environment variables
- Testing your setup
- Troubleshooting

### ▶️ Ready to Run?
**Execute:** [start-slack.sh](start-slack.sh) (Linux/Mac) or [start-slack.bat](start-slack.bat) (Windows)
- Automated setup validation
- Dependency checking
- Token verification
- Safe startup

### ❓ Having Issues?
**Consult:** [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md)
- Connection issues
- Token problems
- No responses from Piddy
- Command failures
- Performance questions
- FAQ section
- Getting help

### 📖 Want to Learn Everything?
**Study:** [Quick Start](QUICKSTART.md) → [README](README.md) → [API.md](API.md) → [CAPABILITIES.md](CAPABILITIES.md)
- Complete feature overview
- API endpoints
- Advanced features
- All command types

---

## 🎯 Quick Navigation

### By Problem

| Issue | Solution |
|-------|----------|
| Piddy doesn't respond | See [SLACK_TROUBLESHOOTING.md - "Piddy Doesn't Respond"](SLACK_TROUBLESHOOTING.md#piddy-doesnt-respond-to-mentions) |
| Connection errors | See [SLACK_TROUBLESHOOTING.md - "Connection refused"](SLACK_TROUBLESHOOTING.md#connection-refused-or-network-error) |
| Token issues | See [SLACK_TROUBLESHOOTING.md - "Invalid token"](SLACK_TROUBLESHOOTING.md#invalid-token-error) |
| Commands fail | See [SLACK_TROUBLESHOOTING.md - "Commands Fail"](SLACK_TROUBLESHOOTING.md#piddy-responds-but-commands-fail) |
| Slow responses | See [SLACK_TROUBLESHOOTING.md - "Slow Responses"](SLACK_TROUBLESHOOTING.md#slow-responses-from-piddy) |
| Setup help | See [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) |

### By Feature

| Feature | Documentation |
|---------|---------------|
| Basic setup | [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) - Steps 1-5 |
| Getting tokens | [SLACK_TROUBLESHOOTING.md - "Get your tokens"](SLACK_TROUBLESHOOTING.md#how-do-i-get-my-tokens) |
| Commands | [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md) - "Common Commands" |
| Using threads | [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md) - "Tips & Tricks" |
| Code blocks | [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md) - "Tips & Tricks" |
| Slash commands | [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) - Step 7C (optional) |
| Docker deployment | [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md#can-i-run-piddy-on-a-servercloud) |
| Multiple instances | [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md#can-i-run-piddy-on-a-servercloud) |
| API usage | [API.md](API.md) |
| Advanced features | [CAPABILITIES.md](CAPABILITIES.md) |

---

## 🏁 Setup Paths

### Path 1: First Time (20 minutes)

1. Read: [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) (10 min)
   - Follow Steps 1-6
   - Copy tokens to `.env`
2. Run: [start-slack.sh](start-slack.sh) or [start-slack.bat](start-slack.bat) (2 min)
3. Test: Open Slack, mention `@Piddy` (3 min)
4. Explore: Check [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md) (5 min)

### Path 2: Fast Setup (5 minutes)

1. Copy tokens to `.env` (know what tokens are already)
2. Run: [start-slack.sh](start-slack.sh) or [start-slack.bat](start-slack.bat)
3. Test: Mention `@Piddy` in Slack
4. If issues: See [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md)

### Path 3: Troubleshooting (varies)

1. Note your error/issue
2. Go to [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md)
3. Find matching section
4. Follow solution steps
5. Test and verify
6. If still stuck: Create issue with error details

### Path 4: Production Deployment (1-2 hours)

1. Read: [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) (10 min)
2. Read: [DEPLOYMENT.md](DEPLOYMENT.md) (20 min)
3. Follow: Docker/Kubernetes setup (30 min)
4. Test: All features in staging (30 min)
5. Deploy: To production (20 min)
6. Monitor: Check logs and usage (10 min)

---

## 📋 Command Cheat Sheet

```bash
# Startup
bash start-slack.sh       # Linux/Mac
start-slack.bat          # Windows
python -m src.main       # Manual start

# Configuration
cat .env                 # View config
export VAR=value        # Set variable
grep SLACK .env         # Show Slack config

# Testing
curl http://localhost:8000/api/v1/agent/health  # Health check
curl http://localhost:8000/api/v1/agent/capabilities  # List capabilities

# Docker
docker build -t piddy .
docker run -p 8000:8000 --env-file .env piddy:latest
docker-compose up -d
```

---

## 🔑 Token Quick Reference

| Token | Format | Where to Get | Purpose |
|-------|--------|-------------|---------|
| `SLACK_BOT_TOKEN` | `xoxb-...` | OAuth & Permissions → Bot User OAuth Token | Send messages to Slack |
| `SLACK_APP_TOKEN` | `xapp-1-...` | Socket Mode → App-Level Token | Listen to Slack events |
| `SLACK_SIGNING_SECRET` | No prefix | Basic Information → Signing Secret | Verify Slack requests |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | https://console.anthropic.com/account/keys | Use Claude AI model |

---

## 🎓 Learning Resources

### For Users
1. [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md) - How to use Piddy
2. [README.md](README.md#slack-integration) - Overview
3. [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md#faq) - FAQ

### For Developers
1. [API.md](API.md) - REST API reference
2. [CAPABILITIES.md](CAPABILITIES.md) - Feature details
3. [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

### For DevOps
1. [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup
2. [Dockerfile](Dockerfile) - Container configuration
3. [docker-compose.yml](docker-compose.yml) - Orchestration

---

## ✅ Pre-Launch Checklist

Before going live, verify:

- [ ] Slack app created at https://api.slack.com/apps
- [ ] Socket Mode enabled
- [ ] Tokens copied correctly:
  - [ ] `SLACK_BOT_TOKEN` starts with `xoxb-`
  - [ ] `SLACK_APP_TOKEN` starts with `xapp-1-`
  - [ ] `SLACK_SIGNING_SECRET` present (no prefix)
- [ ] `ANTHROPIC_API_KEY` set (starts with `sk-ant-`)
- [ ] All in `.env` file
- [ ] Piddy running: `python -m src.main` (no errors)
- [ ] Bot added to channel: `/invite @Piddy`
- [ ] Test message: `@Piddy Hello` → Gets response with ✅
- [ ] Health check passes: `curl http://localhost:8000/api/v1/agent/health`

---

## 🚀 Next Steps

### Beginners
1. Follow [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)
2. Run startup script
3. Try commands in [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md)

### Advanced Users
1. Explore [API.md](API.md) for programmatic access
2. Check [CAPABILITIES.md](CAPABILITIES.md) for advanced features
3. Read [CONTRIBUTING.md](CONTRIBUTING.md) to extend Piddy

### DevOps/SREs
1. Follow [DEPLOYMENT.md](DEPLOYMENT.md)
2. Set up Docker/Kubernetes
3. Configure monitoring and logging

---

## 📞 Getting Help

1. **Check documentation first**: You're probably in the right place!
2. **Search troubleshooting**: [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md)
3. **Check FAQ**: [SLACK_TROUBLESHOOTING.md#faq](SLACK_TROUBLESHOOTING.md#faq)
4. **Create an issue**: With full error details
5. **Contact team**: Your organization's support channel

---

## 📊 Documentation Map

```
README.md (Overview)
    ├── SLACK_QUICK_REFERENCE.md (Commands & Examples)
    ├── SLACK_INTEGRATION.md (Setup Guide)
    ├── SLACK_TROUBLESHOOTING.md (Help & FAQ)
    ├── SLACK_INDEX.md (This file - Navigation)
    │
    ├── QUICKSTART.md (Getting Started)
    ├── API.md (REST API)
    ├── CAPABILITIES.md (Features)
    ├── DEPLOYMENT.md (Production)
    │
    ├── CONTRIBUTING.md (Development)
    ├── BUILD_STATUS.md (CI/CD Status)
    │
    └── src/ (Code)
        ├── agent/core.py (AI Agent)
        ├── integrations/slack_handler.py (Slack Processor)
        └── tools/ (Capabilities)
```

---

**Happy coding with Piddy! 🎉**

For quick answers: [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md)
For setup help: [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)
For troubleshooting: [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md)
